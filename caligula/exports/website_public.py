"""Generate static public JSON for website."""

import json
import math
import pandas as pd
from caligula.config import BACKTEST_DIR, DATA_DIR, TABLES_DIR, WEBSITE_DIR, VALUATION_DATE

# Company metadata sourced from config/universe.yaml
_COMPANY_META = {
    "EOG":  {"company": "EOG Resources",                              "sector": "Energy", "industry": "Oil & Gas Exploration & Production"},
    "FANG": {"company": "Diamondback Energy",                         "sector": "Energy", "industry": "Oil & Gas Exploration & Production"},
    "PXD":  {"company": "Pioneer Natural Resources",                  "sector": "Energy", "industry": "Oil & Gas Exploration & Production"},
    "CTRA": {"company": "Coterra Energy",                             "sector": "Energy", "industry": "Oil & Gas Exploration & Production"},
    "MTDR": {"company": "Matador Resources",                          "sector": "Energy", "industry": "Oil & Gas Exploration & Production"},
    "PR":   {"company": "Permian Resources",                          "sector": "Energy", "industry": "Oil & Gas Exploration & Production"},
    "OVV":  {"company": "Ovintiv",                                    "sector": "Energy", "industry": "Oil & Gas Exploration & Production"},
    "APA":  {"company": "APA Corporation",                            "sector": "Energy", "industry": "Oil & Gas Exploration & Production"},
    "CRGY": {"company": "Crescent Energy",                            "sector": "Energy", "industry": "Oil & Gas Exploration & Production"},
    "SM":   {"company": "SM Energy",                                  "sector": "Energy", "industry": "Oil & Gas Exploration & Production"},
    "VTLE": {"company": "Vital Energy (fka Laredo Petroleum)",        "sector": "Energy", "industry": "Oil & Gas Exploration & Production"},
    "CIVI": {"company": "Civitas Resources",                          "sector": "Energy", "industry": "Oil & Gas Exploration & Production"},
    "CPE":  {"company": "Callon Petroleum",                           "sector": "Energy", "industry": "Oil & Gas Exploration & Production"},
    "CXO":  {"company": "Concho Resources",                           "sector": "Energy", "industry": "Oil & Gas Exploration & Production"},
    "DVN":  {"company": "Devon Energy",                               "sector": "Energy", "industry": "Oil & Gas Exploration & Production"},
    "MRO":  {"company": "Marathon Oil",                               "sector": "Energy", "industry": "Oil & Gas Exploration & Production"},
}

# CSV column name → JSON key short name
_PILLAR_MAP = {
    "unit_economics_score":    "unit_econ",
    "capital_discipline_score": "capital_discipline",
    "balance_sheet_score":     "balance_sheet",
    "hedge_book_score":        "hedge_book",
    "reserves_score":          "reserves",
    "operational_score":       "operational",
    "sentiment_score":         "sentiment",
    "macro_sensitivity_score": "macro",
}

_PILLAR_LABELS = {
    "unit_econ":          "Unit Economics",
    "capital_discipline": "Capital Discipline",
    "balance_sheet":      "Balance Sheet",
    "hedge_book":         "Hedge Book",
    "reserves":           "Reserves",
    "operational":        "Operational",
    "sentiment":          "Sentiment",
    "macro":              "Macro Sensitivity",
}


def _safe_float(v):
    """Return rounded float or None for NaN/missing values."""
    try:
        f = float(v)
        return None if math.isnan(f) or math.isinf(f) else round(f, 6)
    except (TypeError, ValueError):
        return None


def _build_rankings(pillar_df: pd.DataFrame) -> list:
    if pillar_df.empty:
        return []
    latest_q = pillar_df["quarter"].max()
    df = pillar_df[pillar_df["quarter"] == latest_q].sort_values("rank")
    rows = []
    for _, row in df.iterrows():
        entry = {
            "rank":      int(row["rank"]) if pd.notna(row.get("rank")) else None,
            "ticker":    str(row["ticker"]),
            "tier":      str(row["tier"]) if pd.notna(row.get("tier")) else None,
            "composite": _safe_float(row.get("caligula_score")),
        }
        for src_col, dst_key in _PILLAR_MAP.items():
            entry[dst_key] = _safe_float(row.get(src_col))
        rows.append(entry)
    return rows


def _build_backtests(ledger_df: pd.DataFrame) -> dict:
    ep_stats = {}
    if not ledger_df.empty:
        row = ledger_df.iloc[0]
        ep_stats = {
            "cagr":         _safe_float(row.get("cagr")),
            "volatility":   _safe_float(row.get("annualized_volatility")),
            "sharpe":       _safe_float(row.get("sharpe")),
            "max_drawdown": _safe_float(row.get("max_drawdown")),
            "hit_rate":     _safe_float(row.get("hit_rate")),
        }
    return {
        "ep_study": {
            "label":            "Permian Basin E&P Study",
            "stats":            ep_stats,
            "wealth_path":      [],
            "quarterly_returns": [],
        },
        "general_corp": {
            "label":            "General Corporate Equities",
            "stats":            {},
            "wealth_path":      [],
            "quarterly_returns": [],
        },
    }


def _build_deep_dive(pillar_df: pd.DataFrame) -> dict:
    if pillar_df.empty:
        return {}
    result = {}
    for ticker in pillar_df["ticker"].unique():
        ticker_df = pillar_df[pillar_df["ticker"] == ticker].sort_values("quarter")
        meta = _COMPANY_META.get(str(ticker), {
            "company":  str(ticker),
            "sector":   "Unknown",
            "industry": "Unknown",
        })
        latest = ticker_df.iloc[-1]
        composite = _safe_float(latest.get("caligula_score"))
        tier = str(latest["tier"]) if pd.notna(latest.get("tier")) else None

        pillars = {dst_key: _safe_float(latest.get(src_col))
                   for src_col, dst_key in _PILLAR_MAP.items()}

        metrics = [{"metric": "Composite Score", "value": str(composite), "score": composite}]
        for dst_key, label in _PILLAR_LABELS.items():
            v = pillars.get(dst_key)
            metrics.append({"metric": label, "value": str(v), "score": v})

        history = [
            {"quarter": str(row["quarter"]), "score": _safe_float(row.get("caligula_score"))}
            for _, row in ticker_df.iterrows()
        ]

        quality = "high" if composite and composite >= 0.65 else "mid" if composite and composite >= 0.45 else "lower"
        score_str = f"{composite:.2f}" if composite is not None else "N/A"
        narrative = (
            f"{meta['company']} screens as a {quality}-quality operator under the Caligula "
            f"framework with a composite score of {score_str} (Tier {tier})."
        )

        result[str(ticker)] = {
            "ticker":   str(ticker),
            "company":  meta["company"],
            "sector":   meta["sector"],
            "industry": meta["industry"],
            "tier":     tier,
            "composite": composite,
            "pillars":  pillars,
            "metrics":  metrics,
            "history":  history,
            "narrative": narrative,
        }
    return result


def _load_history_df(pillar_df: pd.DataFrame) -> pd.DataFrame:
    """Return a combined dataframe of all historical + latest quarterly scores.

    Priority order (for duplicate ticker+quarter rows): pillar_df (latest export)
    takes precedence over the parquet archive, so the current quarter's data is
    never overwritten by a stale cached value.
    """
    parquet_path = DATA_DIR / "scores" / "all_scores.parquet"
    if not parquet_path.exists():
        return pillar_df.copy()

    hist = pd.read_parquet(parquet_path)
    # Normalise quarter column to plain date string (parquet may store Timestamps)
    hist["quarter"] = pd.to_datetime(hist["quarter"]).dt.strftime("%Y-%m-%d")

    if pillar_df.empty:
        return hist

    # Drop from archive any rows that already exist in pillar_df (ticker+quarter)
    latest_keys = set(zip(pillar_df["ticker"].astype(str), pillar_df["quarter"].astype(str)))
    hist_trimmed = hist[
        ~hist.apply(lambda r: (str(r["ticker"]), str(r["quarter"])) in latest_keys, axis=1)
    ]

    # Align columns: use pillar_df columns as the canonical set
    cols = list(pillar_df.columns)
    hist_aligned = hist_trimmed.reindex(columns=cols)

    return pd.concat([hist_aligned, pillar_df], ignore_index=True)


def export_website_json() -> None:
    """Generates public_caligula_data.json consumed by the Streamlit dashboard."""
    pillar_path = TABLES_DIR / "pillar_scores_quarterly.csv"
    pillar_df = pd.read_csv(pillar_path) if pillar_path.exists() else pd.DataFrame()

    # Full history (archive parquet + latest quarter) used for deep-dive history arrays
    history_df = _load_history_df(pillar_df)

    dcf_path = TABLES_DIR / "eog_dcf_outputs.csv"
    dcf_data = pd.read_csv(dcf_path).to_dict(orient="records") if dcf_path.exists() else []

    ledger_path = BACKTEST_DIR / "performance_ledger.csv"
    ledger_df = pd.read_csv(ledger_path) if ledger_path.exists() else pd.DataFrame()
    ledger_data = ledger_df.to_dict(orient="records") if not ledger_df.empty else []

    payload = {
        "generated_at":     VALUATION_DATE,
        "rankings":         _build_rankings(pillar_df),       # latest quarter only (has rank)
        "backtests":        _build_backtests(ledger_df),
        "deep_dive":        _build_deep_dive(history_df),     # full history
        "dcf_summary":      dcf_data,
        "performance_ledger": ledger_data,
    }

    out_path = WEBSITE_DIR / "public_caligula_data.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


if __name__ == "__main__":
    export_website_json()
