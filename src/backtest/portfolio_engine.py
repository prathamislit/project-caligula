"""Long-short backtest engine with quarterly rebalance."""
import pandas as pd
import numpy as np
from ..ingest.price_client import get_prices


def build_portfolio(score_df: pd.DataFrame, top_pct: float = 0.25, bottom_pct: float = 0.25):
    portfolios = {}
    for q, group in score_df.groupby("quarter"):
        group = group.dropna(subset=["caligula_score"])
        if len(group) < 4:
            continue
        n_long = max(1, int(len(group) * top_pct))
        n_short = max(1, int(len(group) * bottom_pct))
        longs = group.nlargest(n_long, "caligula_score")["ticker"].tolist()
        shorts = group.nsmallest(n_short, "caligula_score")["ticker"].tolist()
        portfolios[q] = {"long": longs, "short": shorts}
    return portfolios


def _ticker_return(ticker: str, start: pd.Timestamp, end: pd.Timestamp):
    px = get_prices(ticker)
    if px is None or px.empty:
        return None
    px["date"] = pd.to_datetime(px["date"])
    px = px.sort_values("date")
    start_px = px[px["date"] >= start]["close"].head(1)
    end_px = px[px["date"] >= end]["close"].head(1)
    if start_px.empty or end_px.empty:
        return None
    return end_px.iloc[0] / start_px.iloc[0] - 1


def compute_returns(portfolios: dict) -> pd.DataFrame:
    results = []
    quarters = sorted(portfolios.keys())
    for i, q in enumerate(quarters[:-1]):
        next_q = quarters[i + 1]
        port = portfolios[q]
        long_rets = [r for t in port["long"]
                     if (r := _ticker_return(t, q, next_q)) is not None]
        short_rets = [r for t in port["short"]
                     if (r := _ticker_return(t, q, next_q)) is not None]
        if long_rets and short_rets:
            results.append({
                "quarter": q,
                "long_return": np.mean(long_rets),
                "short_return": np.mean(short_rets),
                "ls_return": np.mean(long_rets) - np.mean(short_rets),
                "n_long": len(long_rets),
                "n_short": len(short_rets),
            })
    return pd.DataFrame(results)


def performance_stats(returns_df: pd.DataFrame) -> dict:
    if returns_df.empty:
        return {}
    ls = returns_df["ls_return"]
    ann_return = (1 + ls.mean()) ** 4 - 1
    ann_vol = ls.std() * np.sqrt(4)
    sharpe = ann_return / ann_vol if ann_vol > 0 else None
    cum = (1 + ls).cumprod()
    max_dd = (cum / cum.cummax() - 1).min()
    hit_rate = (ls > 0).mean()
    return {
        "ann_return": ann_return,
        "ann_vol": ann_vol,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
        "hit_rate": hit_rate,
        "n_quarters": len(ls),
    }
