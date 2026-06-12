"""Calculate returns for portfolio holdings from real price data."""

import pandas as pd

from caligula.errors import CaligulaBacktestError
from src.ingest.price_client import get_prices


def _holding_period_return(ticker: str, start: pd.Timestamp, end: pd.Timestamp):
    """Total return from first close on/after `start` to first close on/after `end`.

    Returns None when prices are unavailable (e.g. ticker delisted before the
    window) — callers must treat None as a missing observation, not zero.
    """
    px = get_prices(ticker)
    if px is None or px.empty:
        return None
    px = px.copy()
    px["date"] = pd.to_datetime(px["date"])
    px = px.sort_values("date")
    start_px = px[px["date"] >= start]["close"].head(1)
    end_px = px[px["date"] >= end]["close"].head(1)
    if start_px.empty or end_px.empty:
        return None
    return float(end_px.iloc[0] / start_px.iloc[0] - 1)


def calculate_holding_returns(
    holdings_df: pd.DataFrame, holding_period_days: int = 91
) -> pd.DataFrame:
    """Calculate real holding-period returns for each position.

    Each holding entered at `as_of_date` is held for one quarter
    (`holding_period_days`). Prices come from the cached yfinance store
    (data/raw/prices), populated by run_backtest.py.
    """
    if holdings_df.empty:
        return pd.DataFrame()

    returns = []
    for _, row in holdings_df.iterrows():
        start = pd.Timestamp(row["as_of_date"])
        end = start + pd.Timedelta(days=holding_period_days)
        hpr = _holding_period_return(row["ticker"], start, end)
        returns.append(
            {
                "run_id": row["run_id"],
                "start_date": start,
                "end_date": end,
                "ticker": row["ticker"],
                "holding_period_return": (
                    None if hpr is None else hpr * (1 if row["weight"] > 0 else -1)
                ),
            }
        )

    out = pd.DataFrame(returns)
    if out["holding_period_return"].isna().all():
        raise CaligulaBacktestError(
            "No holding returns could be computed — price cache is empty. "
            "Run `python run_backtest.py` to populate data/raw/prices."
        )
    return out
