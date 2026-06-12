"""Pillar 3: Balance Sheet Resilience.
Integrates XBRL financial statements with LLM-parsed credit agreements and maturities."""
import pandas as pd
from .fundamental_quality import _extract_metric, _ttm_value


# Additional XBRL tags needed for balance sheet
BS_TAGS = {
    "long_term_debt": [
        "LongTermDebt",
        "LongTermDebtNoncurrent",
    ],
    "short_term_debt": [
        "LongTermDebtCurrent",
        "DebtCurrent",
    ],
    "cash": [
        "CashAndCashEquivalentsAtCarryingValue",
        "Cash",
    ],
    "interest_expense": [
        "InterestExpense",
        "InterestExpenseDebt",
    ],
    "ebit": [
        "OperatingIncomeLoss",
        "IncomeLossFromContinuingOperationsBeforeInterestExpenseInterestIncomeIncomeTaxesExtraordinaryItemsNoncontrollingInterestsNet",
    ],
    "current_liab": ["LiabilitiesCurrent"],
}


def _extract_bs_metric(facts: dict, our_name: str) -> pd.DataFrame:
    """Same pattern as fundamental_quality but with BS_TAGS lookup."""
    if "facts" not in facts or "us-gaap" not in facts.get("facts", {}):
        return pd.DataFrame()
    for tag in BS_TAGS.get(our_name, []):
        node = facts["facts"]["us-gaap"].get(tag)
        if not node:
            continue
        for unit in ["USD"]:
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


def net_debt_to_ebitdax(facts: dict, as_of: pd.Timestamp):
    """(Long-term + short-term debt - cash) / EBITDAX TTM. Lower is better."""
    ltd_df = _extract_bs_metric(facts, "long_term_debt")
    std_df = _extract_bs_metric(facts, "short_term_debt")
    cash_df = _extract_bs_metric(facts, "cash")
    ebit_df = _extract_bs_metric(facts, "ebit")
    dda_df = _extract_metric(facts, "dda")

    ltd = _ttm_value(ltd_df, as_of, "stock") or 0
    std = _ttm_value(std_df, as_of, "stock") or 0
    cash = _ttm_value(cash_df, as_of, "stock") or 0
    ebit = _ttm_value(ebit_df, as_of, "flow")
    dda = _ttm_value(dda_df, as_of, "flow") or 0

    if ebit is None or ebit == 0:
        return None
    ebitdax = ebit + dda
    net_debt = ltd + std - cash
    return net_debt / ebitdax


def interest_coverage(facts: dict, as_of: pd.Timestamp):
    """EBITDAX TTM / Interest Expense TTM. Higher is better."""
    ebit_df = _extract_bs_metric(facts, "ebit")
    int_df = _extract_bs_metric(facts, "interest_expense")
    dda_df = _extract_metric(facts, "dda")
    
    ebit = _ttm_value(ebit_df, as_of, "flow")
    interest = _ttm_value(int_df, as_of, "flow")
    dda = _ttm_value(dda_df, as_of, "flow") or 0
    
    if ebit is None or interest is None or interest == 0:
        return None
    ebitdax = ebit + dda
    return ebitdax / interest


def debt_maturity_3yr_pct(llm_data: dict):
    """% of total debt maturing within 3 years. Lower is better."""
    if not llm_data:
        return None
    near_term = llm_data.get("debt_maturing_3yr", 0)
    total = llm_data.get("total_debt", 0)
    if not total or total == 0:
        return None
    return float(near_term / total)


def liquidity_to_annual_capex(facts: dict, llm_data: dict, as_of: pd.Timestamp):
    """(Cash + Revolver Availability) / Capex TTM. Higher is better."""
    cash_df = _extract_bs_metric(facts, "cash")
    capex_df = _extract_metric(facts, "capex")
    
    cash = _ttm_value(cash_df, as_of, "stock") or 0
    capex = _ttm_value(capex_df, as_of, "flow")
    
    if capex is None or capex == 0 or not llm_data:
        return None
    
    revolver_cap = llm_data.get("revolver_capacity", 0)
    revolver_out = llm_data.get("revolver_outstanding", 0)
    revolver_avail = max(0.0, revolver_cap - revolver_out)
    
    liquidity = cash + revolver_avail
    return float(liquidity / capex)


def all_balance_sheet_metrics(facts: dict, llm_data: dict, as_of: pd.Timestamp) -> dict:
    return {
        "net_debt_to_ebitdax": net_debt_to_ebitdax(facts, as_of),
        "interest_coverage": interest_coverage(facts, as_of),
        "debt_maturity_3yr_pct": debt_maturity_3yr_pct(llm_data),
        "liquidity_to_annual_capex": liquidity_to_annual_capex(facts, llm_data, as_of),
    }
