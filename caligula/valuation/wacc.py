"""Weighted Average Cost of Capital (WACC) calculations."""

import pandas as pd
from caligula.config import TABLES_DIR, VALUATION_DATE, BOOK_DEBT, SHARES_OUTSTANDING


def calculate_wacc_bridge(
    ticker: str,
    current_price: float,
    beta: float,
    risk_free_rate: float,
    erp: float,
    cost_of_debt: float,
    tax_rate: float,
):
    market_cap = current_price * SHARES_OUTSTANDING
    total_capital = market_cap + BOOK_DEBT

    we = market_cap / total_capital
    wd = BOOK_DEBT / total_capital

    cost_of_equity = risk_free_rate + (beta * erp)
    after_tax_cod = cost_of_debt * (1 - tax_rate)

    wacc = (we * cost_of_equity) + (wd * after_tax_cod)

    bridge = [
        {
            "ticker": ticker,
            "valuation_date": VALUATION_DATE,
            "cost_of_equity": cost_of_equity,
            "cost_of_debt_after_tax": after_tax_cod,
            "weight_equity": we,
            "weight_debt": wd,
            "wacc": wacc,
        }
    ]

    filepath = TABLES_DIR / "eog_wacc_bridge.csv"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(bridge).to_csv(filepath, index=False)

    return wacc
