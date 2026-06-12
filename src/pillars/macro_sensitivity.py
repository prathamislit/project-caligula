"""Pillar 8: Macro Sensitivity Adjustment."""
import pandas as pd
import numpy as np
from ..ingest.price_client import get_prices
from ..ingest.fred_client import get_series


def _get_wti_returns(as_of: pd.Timestamp, days: int = 252):
    """Daily WTI returns ending at as_of."""
    wti = get_series("DCOILWTICO")
    if wti is None or wti.empty:
        return None
    wti = wti.copy()
    wti["date"] = pd.to_datetime(wti["date"])
    wti = wti[wti["date"] <= as_of].sort_values("date").set_index("date")
    if len(wti) < days:
        return None
    return wti["DCOILWTICO"].pct_change().dropna().tail(days)


def _get_ticker_returns(ticker: str, as_of: pd.Timestamp, days: int = 252):
    px = get_prices(ticker)
    if px is None or px.empty:
        return None
    px = px.copy()
    px["date"] = pd.to_datetime(px["date"])
    px = px[px["date"] <= as_of].sort_values("date").set_index("date")
    if len(px) < days:
        return None
    return px["close"].pct_change().dropna().tail(days)


def downside_beta_wti(ticker: str, as_of: pd.Timestamp):
    """Beta on days WTI declined. Higher = more exposed to oil drops."""
    stock_ret = _get_ticker_returns(ticker, as_of)
    wti_ret = _get_wti_returns(as_of)
    if stock_ret is None or wti_ret is None:
        return None
    # Align dates
    aligned = pd.concat([stock_ret.rename("s"), wti_ret.rename("w")], axis=1).dropna()
    if len(aligned) < 50:
        return None
    down_days = aligned[aligned["w"] < 0]
    if len(down_days) < 20:
        return None
    var_w = down_days["w"].var()
    if var_w == 0:
        return None
    cov = np.cov(down_days["s"], down_days["w"])[0, 1]
    return float(cov / var_w)


def realized_vol_relative(ticker: str, as_of: pd.Timestamp, window: int = 63):
    """Stock vol / XOP vol over trailing window."""
    s = _get_ticker_returns(ticker, as_of, days=window)
    x = _get_ticker_returns("XOP", as_of, days=window)
    if s is None or x is None or len(s) < window or len(x) < window:
        return None
    s_vol = s.std() * np.sqrt(252)
    x_vol = x.std() * np.sqrt(252)
    if x_vol == 0:
        return None
    return float(s_vol / x_vol)


def gdelt_basin_sentiment(as_of: pd.Timestamp):
    """Z-score of WTI crude spot prices trailing 30 days vs 252 days as E&P basin drilling sentiment proxy."""
    wti = get_series("DCOILWTICO")
    if wti is None or wti.empty:
        return 0.0
    wti = wti.copy()
    wti["date"] = pd.to_datetime(wti["date"])
    wti = wti[wti["date"] <= as_of].sort_values("date")
    if len(wti) < 252:
        return 0.0
    recent = wti["DCOILWTICO"].tail(30).mean()
    baseline = wti["DCOILWTICO"].tail(252)
    if baseline.std() == 0:
        return 0.0
    return float((recent - baseline.mean()) / baseline.std())


def drawdown_recovery_halflife(ticker: str, as_of: pd.Timestamp):
    """Median days to recover 50% of drawdowns >20% over trailing 5y."""
    px = get_prices(ticker)
    if px is None or px.empty:
        return None
    px = px.copy()
    px["date"] = pd.to_datetime(px["date"])
    px = px[px["date"] <= as_of].sort_values("date").set_index("date")
    px = px.tail(252 * 5)  # 5 years
    if len(px) < 252:
        return None

    closes = px["close"].values
    running_max = np.maximum.accumulate(closes)
    dd = (closes - running_max) / running_max

    episodes = []
    in_dd = False
    trough_idx = None
    peak_val = None

    for i in range(len(closes)):
        if not in_dd and dd[i] < -0.20:
            in_dd = True
            peak_val = running_max[i]
            trough_idx = i
        elif in_dd:
            if closes[i] < closes[trough_idx]:
                trough_idx = i
            half_recovery = closes[trough_idx] + 0.5 * (peak_val - closes[trough_idx])
            if closes[i] >= half_recovery:
                episodes.append(i - trough_idx)
                in_dd = False

    if not episodes:
        return None
    return float(np.median(episodes))


def all_macro_metrics(ticker: str, as_of: pd.Timestamp) -> dict:
    return {
        "downside_beta_wti": downside_beta_wti(ticker, as_of),
        "realized_vol_relative": realized_vol_relative(ticker, as_of),
        "gdelt_basin_sentiment": gdelt_basin_sentiment(as_of),
        "drawdown_recovery_halflife": drawdown_recovery_halflife(ticker, as_of),
    }
