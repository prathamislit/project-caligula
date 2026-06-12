"""Pillar 5: Reserve & Inventory Quality."""
import pandas as pd
from .fundamental_quality import _extract_metric, _ttm_value, _market_cap
from .balance_sheet import _extract_bs_metric


def pd_to_total_proved(llm_data: dict):
    """Proved Developed / Total Proved reserves. Higher is better (lower development risk)."""
    if not llm_data:
        return None
    pd_res = llm_data.get("proved_developed_mmboe", 0) or 0
    total = llm_data.get("total_proved_mmboe", 0) or 0
    if total == 0:
        return None
    return float(pd_res / total)


def reserve_replacement_3yr(llm_data: dict):
    """3-year Organic Reserve Replacement Rate (Extensions & Discoveries / Production)."""
    if not llm_data:
        return None
    additions = llm_data.get("additions_3yr_mmboe", 0) or 0
    prod = llm_data.get("production_mmboe", 0) or 0
    if prod == 0:
        return None
    # 3-year addition / 3 years of production
    return float(additions / (prod * 3))


def tier1_inventory_years(llm_data: dict):
    """Company disclosed Tier-1 drilling inventory life in years. Higher is better."""
    if not llm_data or "tier1_years" not in llm_data:
        return None
    return float(llm_data["tier1_years"])


def pv10_to_ev(llm_data: dict, facts: dict, ticker: str, as_of: pd.Timestamp):
    """PV-10 Reserve Value / Enterprise Value. Higher represents deep valuation discount."""
    if not llm_data or "pv10_usd" not in llm_data:
        return None
    
    pv10 = llm_data["pv10_usd"]
    
    # Calculate Enterprise Value: Market Cap + Long Debt + Short Debt - Cash
    ltd_df = _extract_bs_metric(facts, "long_term_debt")
    std_df = _extract_bs_metric(facts, "short_term_debt")
    cash_df = _extract_bs_metric(facts, "cash")
    shares_df = _extract_metric(facts, "shares_out")
    
    ltd = _ttm_value(ltd_df, as_of, "stock") or 0
    std = _ttm_value(std_df, as_of, "stock") or 0
    cash = _ttm_value(cash_df, as_of, "stock") or 0
    shares = _ttm_value(shares_df, as_of, "stock")
    
    if not shares:
        return None
        
    mcap = _market_cap(ticker, as_of, shares)
    if not mcap:
        return None
        
    ev = mcap + ltd + std - cash
    if ev <= 0:
        return None
        
    return float(pv10 / ev)


def all_reserves_metrics(llm_data: dict, facts: dict, ticker: str, as_of: pd.Timestamp) -> dict:
    return {
        "pd_to_total_proved": pd_to_total_proved(llm_data),
        "reserve_replacement_3yr": reserve_replacement_3yr(llm_data),
        "tier1_inventory_years": tier1_inventory_years(llm_data),
        "pv10_to_ev": pv10_to_ev(llm_data, facts, ticker, as_of),
    }
