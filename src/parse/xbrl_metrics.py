"""Standard XBRL metric extraction for E&P companies."""
from .tenk_parser import extract_xbrl_metric

XBRL_TAGS = {
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"],
    "net_income": ["NetIncomeLoss"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "capex": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireOilAndGasProperty",
    ],
    "total_debt": ["LongTermDebt", "LongTermDebtNoncurrent"],
    "cash": ["CashAndCashEquivalentsAtCarryingValue"],
    "interest_expense": ["InterestExpense"],
    "dda": ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization"],
    "stock_repurchase": ["PaymentsForRepurchaseOfCommonStock"],
    "dividends_paid": ["PaymentsOfDividendsCommonStock", "PaymentsOfDividends"],
    "shares_outstanding": ["CommonStockSharesOutstanding"],
}


def get_metric_series(facts: dict, our_name: str):
    tags = XBRL_TAGS.get(our_name, [])
    for tag in tags:
        df = extract_xbrl_metric(facts, tag)
        if df is not None and not df.empty:
            df["our_metric"] = our_name
            df["xbrl_tag"] = tag
            return df
    return None
