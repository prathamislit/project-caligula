"""Pillar 1: Momentum & Technicals.
All inputs from cached yfinance data. Zero external API calls."""
import pandas as pd
import numpy as np
from ..ingest.price_client import get_prices


def _aligned_prices(ticker: str, benchmark: str, as_of: pd.Timestamp):
    """Fetch and align ticker + benchmark prices up to as_of date."""
    t = get_prices(ticker)
    b = get_prices(benchmark)
    if t is None or b is None or t.empty or b.empty:
        return None, None
    t = t.copy()
    b = b.copy()
    t["date"] = pd.to_datetime(t["date"])
    b["date"] = pd.to_datetime(b["date"])
    t = t[t["date"] <= as_of].set_index("date").sort_index()
    b = b[b["date"] <= as_of].set_index("date").sort_index()
    if t.empty or b.empty:
        return None, None
    return t, b


def return_vs_benchmark(ticker: str, benchmark: str, as_of: pd.Timestamp, lookback_days: int):
    """Excess return of ticker over benchmark, lookback_days ending at as_of."""
    t, b = _aligned_prices(ticker, benchmark, as_of)
    if t is None or len(t) < lookback_days or len(b) < lookback_days:
        return None
    t_ret = t["close"].iloc[-1] / t["close"].iloc[-lookback_days] - 1
    b_ret = b["close"].iloc[-1] / b["close"].iloc[-lookback_days] - 1
    return float(t_ret - b_ret)


def return_6m_vs_xop(ticker: str, as_of: pd.Timestamp):
    return return_vs_benchmark(ticker, "XOP", as_of, 126)


def return_12m_vs_xop(ticker: str, as_of: pd.Timestamp):
    return return_vs_benchmark(ticker, "XOP", as_of, 252)


def vol_relative_sector(ticker: str, as_of: pd.Timestamp, window: int = 90):
    """Annualized realized vol of ticker / sector ETF."""
    t, b = _aligned_prices(ticker, "XOP", as_of)
    if t is None or len(t) < window or len(b) < window:
        return None
    t_ret = t["close"].pct_change().tail(window)
    b_ret = b["close"].pct_change().tail(window)
    t_vol = t_ret.std() * np.sqrt(252)
    b_vol = b_ret.std() * np.sqrt(252)
    if b_vol == 0 or pd.isna(b_vol):
        return None
    return float(t_vol / b_vol)


def distance_from_52w_high(ticker: str, as_of: pd.Timestamp):
    """Negative number. -0.05 = 5% below 52w high. Closer to 0 is better."""
    t = get_prices(ticker)
    if t is None or t.empty:
        return None
    t = t.copy()
    t["date"] = pd.to_datetime(t["date"])
    t = t[t["date"] <= as_of].sort_values("date")
    if len(t) < 252:
        return None
    last_252 = t.tail(252)
    high = last_252["close"].max()
    current = last_252["close"].iloc[-1]
    if high == 0:
        return None
    return float(current / high - 1)


def ma_50_200_signal(ticker: str, as_of: pd.Timestamp):
    """Returns 1 if 50DMA > 200DMA (golden cross territory), 0 otherwise.
    Continuous version: (50DMA - 200DMA) / 200DMA."""
    t = get_prices(ticker)
    if t is None or t.empty:
        return None
    t = t.copy()
    t["date"] = pd.to_datetime(t["date"])
    t = t[t["date"] <= as_of].sort_values("date")
    if len(t) < 200:
        return None
    ma50 = t["close"].tail(50).mean()
    ma200 = t["close"].tail(200).mean()
    if ma200 == 0:
        return None
    return float((ma50 - ma200) / ma200)


def all_momentum_metrics(ticker: str, as_of: pd.Timestamp) -> dict:
    """Compute all momentum metrics for a ticker at a given quarter-end."""
    return {
        "return_6m_vs_xop": return_6m_vs_xop(ticker, as_of),
        "return_12m_vs_xop": return_12m_vs_xop(ticker, as_of),
        "vol_relative_sector": vol_relative_sector(ticker, as_of),
        "distance_from_52w_high": distance_from_52w_high(ticker, as_of),
        "ma_50_200_signal": ma_50_200_signal(ticker, as_of),
    }
