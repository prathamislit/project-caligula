"""Quarter and date helpers for backtesting."""
import pandas as pd


def quarter_ends(start: str, end: str):
    return pd.date_range(start, end, freq="QE")


def as_of_quarter(d) -> str:
    ts = pd.Timestamp(d)
    return f"{ts.year}Q{ts.quarter}"


def quarter_to_date(q: str) -> pd.Timestamp:
    year, qnum = q.split("Q")
    month = int(qnum) * 3
    return pd.Timestamp(year=int(year), month=month, day=1) + pd.offsets.MonthEnd(0)
