"""Global configuration and paths for Caligula."""

import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def env(key: str, required: bool = True) -> str:
    val = os.getenv(key)
    if required and not val:
        raise ValueError(f"Missing required environment variable: {key}")
    return val or ""


# --- Paths ---
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
AUDIT_DIR = DATA_DIR / "audit"
LEDGERS_DIR = DATA_DIR / "ledgers"
VALIDATION_DIR = DATA_DIR / "validation"
EXTRACTED_DIR = DATA_DIR / "extracted"
UNIVERSE_DIR = DATA_DIR / "universe"
METHODOLOGY_DIR = DATA_DIR / "methodology"
BACKTEST_DIR = DATA_DIR / "backtest"

OUTPUTS_DIR = ROOT / "outputs"
TABLES_DIR = OUTPUTS_DIR / "tables"
CHARTS_DIR = OUTPUTS_DIR / "charts"
MEMOS_DIR = OUTPUTS_DIR / "memos"
WEBSITE_DIR = OUTPUTS_DIR / "website"

# Create directories dynamically if needed during runtime (though Makefile handles this)
for d in [
    AUDIT_DIR,
    RAW_DIR,
    PROCESSED_DIR,
    LEDGERS_DIR,
    VALIDATION_DIR,
    EXTRACTED_DIR,
    UNIVERSE_DIR,
    METHODOLOGY_DIR,
    BACKTEST_DIR,
    TABLES_DIR,
    CHARTS_DIR,
    MEMOS_DIR,
    WEBSITE_DIR,
]:
    d.mkdir(parents=True, exist_ok=True)

# --- Canonical Configuration ---
VALUATION_DATE = "2026-06-10"
MARKET_DATA_AS_OF = "2026-06-06"
SIGNAL_LAG_DAYS = 45
REBALANCE_FREQUENCY = "quarterly"
TRANSACTION_COST_BPS = 5.0
SHORT_BORROW_BPS = 50.0
BENCHMARK_TICKER = "XOP"
OIL_PRICE_SOURCE = "CME_WTI"
GAS_PRICE_SOURCE = "CME_HH"
RISK_FREE_RATE_SOURCE = "FRED_10Y"
GEMINI_MODEL_NAME = "gemini-1.5-flash"
GEMINI_PROMPT_VERSION = "v1"

# Extract configurations for valuation
BOOK_DEBT = 3778000000.0
CASH = 5275000000.0
SHARES_OUTSTANDING = 578000000.0

HYPERBOLIC_B = 0.9
INITIAL_DECLINE_DI = 0.25
WTI_LONG_RUN = 68.50
OIL_DIFF = -0.02
GAS_DIFF = -0.15
TAX_RATE = 0.21
