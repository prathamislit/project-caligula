"""Pillar 2: Fundamental Quality.
Real XBRL integration. Point-in-time aware."""
import pandas as pd
import numpy as np
from ..ingest.edgar_client import get_company_facts
from ..ingest.price_client import get_prices


# XBRL tag mappings — try each in order, use first that returns data
TAGS = {
    "ocf": ["NetCashProvidedByUsedInOperatingActivities"],
    "capex": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireOilAndGasProperty",
    ],
    "dda": [
        "DepreciationDepletionAndAmortization",
        "DepreciationAndAmortization",
    ],
    "buybacks": ["PaymentsForRepurchaseOfCommonStock"],
    "dividends": [
        "PaymentsOfDividendsCommonStock",
        "PaymentsOfDividends",
    ],
    "shares_out": [
        "CommonStockSharesOutstanding",
        "EntityCommonStockSharesOutstanding",
    ],
}


def _extract_metric(facts: dict, our_name: str) -> pd.DataFrame:
    """Pull XBRL metric, return DataFrame with end_date, value, period."""
    if "facts" not in facts or "us-gaap" not in facts.get("facts", {}):
        return pd.DataFrame()

    for tag in TAGS.get(our_name, []):
        node = facts["facts"]["us-gaap"].get(tag)
        if not node:
            continue
        # Try USD first, then shares
        for unit in ["USD", "shares", "USD/shares"]:
            if unit not in node.get("units", {}):
                continue
            rows = node["units"][unit]
            df = pd.DataFrame(rows)
            if df.empty:
                continue
            df["end"] = pd.to_datetime(df["end"])
            if "start" in df.columns:
                df["start"] = pd.to_datetime(df["start"])
            df["xbrl_tag"] = tag
            df["our_metric"] = our_name
            return df
    return pd.DataFrame()


def _ttm_value(df: pd.DataFrame, as_of: pd.Timestamp, flow_or_stock: str = "flow"):
    """For flow metrics (OCF, capex, dividends): sum last 4 quarters ending <= as_of.
    For stock metrics (shares out, debt): latest value <= as_of."""
    if df.empty:
        return None

    # Filter to "as available at as_of" — filings must have been published before as_of
    # XBRL doesn't tell us the filing date directly. Use end_date + 90 day reporting lag as proxy.
    LAG_DAYS = 90
    df = df[df["end"] <= as_of - pd.Timedelta(days=LAG_DAYS)]
    if df.empty:
        return None

    if flow_or_stock == "stock":
        latest = df.sort_values("end").iloc[-1]
        return float(latest["val"])

    # Flow: sum quarterly periods covering last 12 months
    # Filter to quarterly periods (start to end is ~90 days)
    if "start" in df.columns:
        df = df.copy()
        df["period_days"] = (df["end"] - df["start"]).dt.days
        quarterly = df[(df["period_days"] >= 80) & (df["period_days"] <= 100)]
        if not quarterly.empty:
            # Get last 4 quarterly values
            quarterly = quarterly.sort_values("end").drop_duplicates("end", keep="last")
            last_4 = quarterly.tail(4)
            if len(last_4) >= 3:
                return float(last_4["val"].sum())

        # Fall back to annual (period ~365 days)
        annual = df[(df["period_days"] >= 350) & (df["period_days"] <= 380)]
        if not annual.empty:
            latest = annual.sort_values("end").iloc[-1]
            return float(latest["val"])

    return None


def _market_cap(ticker: str, as_of: pd.Timestamp, shares_out: float):
    """Market cap at as_of date."""
    if not shares_out:
        return None
    px = get_prices(ticker)
    if px is None or px.empty:
        return None
    px = px.copy()
    px["date"] = pd.to_datetime(px["date"])
    px = px[px["date"] <= as_of].sort_values("date")
    if px.empty:
        return None
    last_close = px["close"].iloc[-1]
    return float(last_close * shares_out)


def fcf_yield_ttm(facts: dict, ticker: str, as_of: pd.Timestamp):
    """(OCF TTM - CapEx TTM) / Market Cap."""
    ocf_df = _extract_metric(facts, "ocf")
    capex_df = _extract_metric(facts, "capex")
    shares_df = _extract_metric(facts, "shares_out")

    ocf = _ttm_value(ocf_df, as_of, "flow")
    capex = _ttm_value(capex_df, as_of, "flow")
    shares = _ttm_value(shares_df, as_of, "stock")

    if ocf is None or capex is None or shares is None:
        return None
    mcap = _market_cap(ticker, as_of, shares)
    if mcap is None or mcap == 0:
        return None
    return (ocf - capex) / mcap


def capex_to_dda(facts: dict, as_of: pd.Timestamp):
    """CapEx TTM / DDA TTM. Lower is more disciplined."""
    capex_df = _extract_metric(facts, "capex")
    dda_df = _extract_metric(facts, "dda")
    capex = _ttm_value(capex_df, as_of, "flow")
    dda = _ttm_value(dda_df, as_of, "flow")
    if capex is None or dda is None or dda == 0:
        return None
    return capex / dda


def capital_return_yield(facts: dict, ticker: str, as_of: pd.Timestamp):
    """(Buybacks + Dividends TTM) / Market Cap."""
    bb_df = _extract_metric(facts, "buybacks")
    div_df = _extract_metric(facts, "dividends")
    shares_df = _extract_metric(facts, "shares_out")

    bb = _ttm_value(bb_df, as_of, "flow") or 0
    div = _ttm_value(div_df, as_of, "flow") or 0
    shares = _ttm_value(shares_df, as_of, "stock")

    if shares is None:
        return None
    mcap = _market_cap(ticker, as_of, shares)
    if mcap is None or mcap == 0:
        return None
    return (bb + div) / mcap


def ocf_growth_yoy(facts: dict, as_of: pd.Timestamp):
    """OCF TTM vs OCF TTM 1 year ago. Growth rate."""
    ocf_df = _extract_metric(facts, "ocf")
    current = _ttm_value(ocf_df, as_of, "flow")
    prior = _ttm_value(ocf_df, as_of - pd.Timedelta(days=365), "flow")
    if current is None or prior is None or prior == 0:
        return None
    return (current - prior) / abs(prior)


def all_fundamental_metrics(cik: str, ticker: str, as_of: pd.Timestamp) -> dict:
    """Compute all fundamental quality metrics."""
    try:
        facts = get_company_facts(cik)
    except Exception:
        return {k: None for k in [
            "fcf_yield_ttm", "capex_to_dda", "capital_return_yield", "ocf_growth_yoy"
        ]}

    return {
        "fcf_yield_ttm": fcf_yield_ttm(facts, ticker, as_of),
        "capex_to_dda": capex_to_dda(facts, as_of),
        "capital_return_yield": capital_return_yield(facts, ticker, as_of),
        "ocf_growth_yoy": ocf_growth_yoy(facts, as_of),
    }
