"""Insider transaction parsing from Form 4 XML."""
import pandas as pd
from ..ingest.edgar_client import get_filing_index

PURCHASE_CODES = {"P"}
SALE_CODES = {"S", "S+"}


def get_insider_transactions_6mo(cik: str, as_of_date: str):
    """Aggregate net insider buying $ over trailing 6 months."""
    filings = get_filing_index(cik, "4")
    cutoff = pd.Timestamp(as_of_date)
    six_mo_ago = cutoff - pd.DateOffset(months=6)
    window = [f for f in filings
              if six_mo_ago <= pd.Timestamp(f["date"]) <= cutoff]
    # Stub: XML parse of each filing would extract transaction codes, shares, price
    # Full implementation requires fetching and parsing each accession's XML
    return {
        "net_purchase_usd": 0,
        "buyer_count": 0,
        "filing_count": len(window),
        "note": "Full XML parse is Phase 2 — placeholder returns zero net buying",
    }
