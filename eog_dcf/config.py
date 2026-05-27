# Valuation Configurations for EOG Resources DCF Model

VALUATION_DATE = "2026-06-10"
TICKER = "EOG"

# Market Inputs
SHARES_OUTSTANDING = 532.63  # USD Millions
CURRENT_PRICE = 141.22
MARKET_CAP = SHARES_OUTSTANDING * CURRENT_PRICE

# Balance Sheet Inputs (LTM / FY25 locked)
BOOK_DEBT = 8318.0
CASH = 3396.0
NET_DEBT = BOOK_DEBT - CASH

# Cost of Capital
RISK_FREE_RATE = 0.0425
ERP = 0.055
BETA = 0.943
TAX_RATE = 0.21
PRETAX_COST_OF_DEBT = 0.035

# CapEx and D&A Parameters
SUSTAINING_CAPEX_PCT = 0.85
DDA_PER_BOE = 15.5

# Commodity curves & differentials
WTI_LONG_RUN = 65.0
HH_LONG_RUN = 3.0
OIL_DIFF = -0.02
GAS_DIFF = -0.15
NGL_REALIZATION = 0.35

# Decline curve parameters
HYPERBOLIC_B = 0.9
INITIAL_DECLINE_DI = 0.25

# Exit multiple TV method
EXIT_MULTIPLE = 5.5
