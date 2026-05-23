"""SEC EDGAR client for 10-K, 10-Q, Form 4, 13F."""
import requests
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from ..utils.config import env
from ..utils.io import write_cache, read_cache

BASE = "https://data.sec.gov"
ARCHIVES = "https://www.sec.gov/Archives"


def _headers():
    return {"User-Agent": env("SEC_USER_AGENT"), "Accept-Encoding": "gzip, deflate"}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _get(url: str):
    r = requests.get(url, headers=_headers(), timeout=30)
    r.raise_for_status()
    time.sleep(0.15)  # SEC rate limit: 10 req/sec
    return r


def get_company_facts(cik: str):
    key = f"facts_{cik}"
    cached = read_cache("edgar", key, "json")
    if cached:
        return cached
    cik_padded = cik.zfill(10)
    url = f"{BASE}/api/xbrl/companyfacts/CIK{cik_padded}.json"
    data = _get(url).json()
    write_cache(data, "edgar", key, "json")
    return data


def get_submissions(cik: str):
    key = f"sub_{cik}"
    cached = read_cache("edgar", key, "json")
    if cached:
        return cached
    cik_padded = cik.zfill(10)
    url = f"{BASE}/submissions/CIK{cik_padded}.json"
    data = _get(url).json()
    write_cache(data, "edgar", key, "json")
    return data


def get_filing_index(cik: str, form_type: str):
    subs = get_submissions(cik)
    recent = subs.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accs = recent.get("accessionNumber", [])
    docs = recent.get("primaryDocument", [])
    out = []
    for i, f in enumerate(forms):
        if f == form_type:
            out.append({
                "accession": accs[i],
                "date": dates[i],
                "document": docs[i],
            })
    return out


def fetch_filing_document(cik: str, accession: str, document: str):
    key = f"{cik}_{accession}_{document}"
    cached = read_cache("edgar", key, "html")
    if cached:
        return cached
    acc_clean = accession.replace("-", "")
    url = f"{ARCHIVES}/edgar/data/{int(cik)}/{acc_clean}/{document}"
    text = _get(url).text
    write_cache(text, "edgar", key, "html")
    return text


def get_cik_for_ticker(ticker: str) -> str:
    """Look up CIK for a given US stock ticker symbol via the SEC public tickers map."""
    ticker = ticker.upper().strip()
    cached_mapping = read_cache("edgar", "ticker_cik_map", "json")
    if not cached_mapping:
        try:
            url = "https://www.sec.gov/files/company_tickers.json"
            raw_data = _get(url).json()
            mapping = {}
            for item in raw_data.values():
                mapping[item["ticker"]] = str(item["cik_str"])
            write_cache(mapping, "edgar", "ticker_cik_map", "json")
            cached_mapping = mapping
        except Exception as e:
            print(f"WARN CIK ticker lookup map download failed: {e}")
            return ""
    return cached_mapping.get(ticker, "")

