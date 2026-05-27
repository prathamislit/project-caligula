from ..config import RISK_FREE_RATE, ERP, BETA, TAX_RATE, PRETAX_COST_OF_DEBT, MARKET_CAP, BOOK_DEBT

def calculate_wacc():
    # Cost of Equity (CAPM)
    re = RISK_FREE_RATE + (BETA * ERP)
    
    # Cost of Debt (After-tax)
    rd_aftertax = PRETAX_COST_OF_DEBT * (1 - TAX_RATE)
    
    # Capitalization Weights
    v = MARKET_CAP + BOOK_DEBT
    we = MARKET_CAP / v
    wd = BOOK_DEBT / v
    
    # WACC
    wacc = (we * re) + (wd * rd_aftertax)
    return wacc, re, rd_aftertax, we, wd
