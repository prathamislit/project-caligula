"""Pillar 2: Capital Discipline."""
import pandas as pd
from .fundamental_quality import _extract_metric, _ttm_value, _market_cap


def capex_to_dda(facts: dict, as_of: pd.Timestamp):
    """CapEx TTM / DDA TTM. Lower is more disciplined."""
    capex_df = _extract_metric(facts, "capex")
    dda_df = _extract_metric(facts, "dda")
    capex = _ttm_value(capex_df, as_of, "flow")
    dda = _ttm_value(dda_df, as_of, "flow")
    if capex is None or dda is None or dda == 0:
        return None
    return capex / dda


def fcf_yield_ttm(facts: dict, ticker: str, as_of: pd.Timestamp):
    """FCF TTM / Market Cap."""
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


def buyback_timing_quality(facts: dict, as_of: pd.Timestamp):
    """Compare buyback activity vs cash flow trend.
    Positive value indicates capital discipline in repurchases."""
    bb_df = _extract_metric(facts, "buybacks")
    ocf_df = _extract_metric(facts, "ocf")
    bb = _ttm_value(bb_df, as_of, "flow") or 0
    ocf = _ttm_value(ocf_df, as_of, "flow") or 0
    if ocf == 0 or bb == 0:
        return 0.0
    return float(bb / ocf)


def all_capital_discipline_metrics(facts: dict, ticker: str, as_of: pd.Timestamp) -> dict:
    return {
        "capex_to_dda": capex_to_dda(facts, as_of),
        "fcf_yield_ttm": fcf_yield_ttm(facts, ticker, as_of),
        "capital_return_yield": capital_return_yield(facts, ticker, as_of),
        "buyback_timing_quality": buyback_timing_quality(facts, as_of),
    }
