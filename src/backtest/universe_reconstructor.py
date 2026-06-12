"""Reconstruct point-in-time universe for each quarter."""
import pandas as pd
from ..utils.config import load_universe
from ..utils.dates import quarter_ends


def active_universe_at(as_of: pd.Timestamp) -> list:
    uni = load_universe()["permian_universe"]
    active = []
    for c in uni:
        start = pd.Timestamp(c["start_date"])
        end = pd.Timestamp(c["end_date"]) if c["end_date"] else pd.Timestamp("2099-01-01")
        if start <= as_of <= end:
            active.append(c)
    return active


def quarter_universe_table(start="2014-01-01", end="2025-12-31") -> pd.DataFrame:
    rows = []
    for q in quarter_ends(start, end):
        for c in active_universe_at(q):
            rows.append({"quarter": q, **c})
    return pd.DataFrame(rows)
