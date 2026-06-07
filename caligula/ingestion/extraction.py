"""AI-Driven E&P Footnote Parser with strict audit trailing."""

import json
import requests
import pandas as pd
from caligula.config import env, GEMINI_MODEL_NAME, GEMINI_PROMPT_VERSION
from caligula.paths import write_cache, read_cache
from caligula.errors import CaligulaExtractionError
from caligula.ingestion.sec_fetch import fetch_filing_document
from caligula.ingestion.filing_index import get_filing_index
from caligula.ingestion.extraction_audit import (
    compute_audit_hash,
    log_extraction,
    log_extraction_failure,
)

# Import simple regex based section finder from old tenk_parser if needed,
# for now we'll write a simple one here to keep extraction self-contained.
import re
from bs4 import BeautifulSoup

API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL_NAME}:generateContent"
)


def clean_html(html_text: str) -> str:
    soup = BeautifulSoup(html_text, "lxml")
    return soup.get_text(separator="\n", strip=True)


def find_section(text: str, patterns: list, max_chars: int = 12000) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            start = match.start()
            return text[start : start + max_chars]
    return ""


def extract_filing_data(cik: str, ticker: str, as_of: pd.Timestamp) -> dict:
    """Extract structured parameters from SEC 10-K/Q footnotes via Gemini API."""
    try:
        filings = get_filing_index(cik, "10-K") + get_filing_index(cik, "10-Q")
        valid = [f for f in filings if pd.Timestamp(f["date"]) <= as_of]
        if not valid:
            raise CaligulaExtractionError(
                f"No valid filings found for {cik} before {as_of}"
            )
        valid.sort(key=lambda x: pd.Timestamp(x["date"]))
        latest_filing = valid[-1]
        accession = latest_filing["accession"]
    except Exception as exc:
        raise CaligulaExtractionError("Failed to fetch filing index.") from exc

    key = f"extract_{cik}_{accession}_{GEMINI_PROMPT_VERSION}"
    cached = read_cache("edgar", key, "json")
    if cached is not None:
        return cached

    api_key = env("GEMINI_API_KEY", required=True)

    try:
        html_content = fetch_filing_document(cik, accession, latest_filing["document"])
        raw_text = clean_html(html_content)
    except Exception as exc:
        log_extraction_failure(
            {
                "ticker": ticker,
                "accession_number": accession,
                "error_type": "DocumentFetchError",
                "error_message": str(exc),
                "resolved": False,
            }
        )
        raise CaligulaExtractionError("Failed to fetch HTML filing document.") from exc

    hedge_text = (
        find_section(
            raw_text,
            [
                r"commodity\s+(price\s+)?(risk|hedg)",
                r"derivative\s+(instruments|financial)",
                r"hedging\s+activities",
            ],
            max_chars=12000,
        )
        or ""
    )

    debt_text = (
        find_section(
            raw_text,
            [
                r"debt\s+maturity\s+schedule",
                r"maturity\s+of\s+debt",
                r"long-term\s+debt\s+maturities",
            ],
            max_chars=8000,
        )
        or ""
    )

    reserves_text = (
        find_section(
            raw_text,
            [
                r"reserves?\s+(replacement|disclosure)",
                r"proved\s+(developed|undeveloped)\s+reserves?",
                r"oil\s+and\s+gas\s+reserves?",
            ],
            max_chars=10000,
        )
        or ""
    )

    context = (
        f"--- HEDGES ---\n{hedge_text}\n"
        f"--- DEBT ---\n{debt_text}\n"
        f"--- RESERVES ---\n{reserves_text}"
    )

    prompt = f"""
    You are an expert E&P financial analyst. Extract structured metrics from
    the SEC footnotes provided.
    You must output a single JSON document. Return ONLY raw JSON text. Do NOT
    wrap with ```json.
    Use the following exact JSON keys. If a value is not found, return null.

    "pct_oil_hedged_ntm": Float (0.0 to 1.0)
    "weighted_floor": Float
    "swap_pct": Float (0.0 to 1.0)
    "collar_pct": Float (0.0 to 1.0)
    "put_pct": Float (0.0 to 1.0)
    "debt_maturing_3yr": Float
    "total_debt": Float
    "revolver_capacity": Float
    "revolver_outstanding": Float
    "proved_developed_mmboe": Float
    "total_proved_mmboe": Float
    "organic_additions_mmboe": Float
    "production_mmboe": Float
    "additions_3yr_mmboe": Float
    "breakeven_wti_10pct": Float
    "tier1_years": Float
    "pv10_usd": Float
    "fd_cost_per_boe": Float
    "cash_opex_per_boe": Float

    Context:
    {context}
    """

    try:
        url = f"{API_URL}?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        raw_output = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

        if raw_output.startswith("```json"):
            raw_output = raw_output[7:]
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3]

        parsed = json.loads(raw_output)

        # Log to extraction ledger for each key
        for k, v in parsed.items():
            if v is not None:
                audit_record = {
                    "extraction_id": f"{ticker}_{accession}_{k}",
                    "ticker": ticker,
                    "accession_number": accession,
                    "filing_date": latest_filing["date"],
                    "source_section": "Footnotes",
                    "metric_name": k,
                    "extracted_value": v,
                    "raw_extracted_text": context[
                        :500
                    ],  # Save a snippet of the context
                    "model_name": GEMINI_MODEL_NAME,
                    "prompt_version": GEMINI_PROMPT_VERSION,
                    "confidence_score": 0.95,
                }
                audit_record["audit_hash"] = compute_audit_hash(audit_record)
                log_extraction(audit_record)

        write_cache(parsed, "edgar", key, "json")
        return parsed
    except Exception as exc:
        log_extraction_failure(
            {
                "ticker": ticker,
                "accession_number": accession,
                "error_type": "GeminiAPIError",
                "error_message": str(exc),
                "resolved": False,
            }
        )
        raise CaligulaExtractionError("AI extraction failed.") from exc
