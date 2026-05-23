"""v2: End-to-end backtest runner."""
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
from pathlib import Path
from src.utils.config import load_universe, DATA_DIR
from src.ingest.price_client import get_prices
from src.backtest.score_history import run_backtest_scoring
from src.backtest.portfolio_engine import build_portfolio, compute_returns, performance_stats


def ensure_prices_cached():
    """Pre-cache prices for universe + benchmarks."""
    uni = load_universe()
    tickers = [c["ticker"] for c in uni["permian_universe"]]
    general_tickers = ["AAPL", "MSFT", "GOOG", "AMZN", "NFLX", "NVDA", "TSLA", "META", "WMT", "DIS", "JPM", "V", "PG", "JNJ"]
    benchmarks = ["XOP", "SPY", "CL=F"]
    all_tickers = sorted(list(set(tickers + general_tickers + benchmarks)))
    print(f"Caching prices for {len(all_tickers)} symbols...")
    for t in all_tickers:
        p = get_prices(t)
        status = "OK" if p is not None else "MISSING"
        print(f"  {t}... {status}")


def main():
    ensure_prices_cached()

    print("\nRunning quarterly Permian E&P backtest scoring...")
    scores = run_backtest_scoring()

    print("\nRunning quarterly General Corporate backtest scoring...")
    from src.backtest.score_history import run_general_backtest_scoring
    general_scores = run_general_backtest_scoring()

    if scores is None or scores.empty:
        print("Backtest failed — no Permian scores generated.")
        return

    # Build Permian E&P Backtest
    print("\nBuilding Permian E&P L/S portfolio and computing returns...")
    portfolios = build_portfolio(scores, top_pct=0.25, bottom_pct=0.25)
    returns = compute_returns(portfolios)
    stats = performance_stats(returns)

    # Build General Corporate Backtest
    print("Building General Corporate L/S portfolio and computing returns...")
    general_portfolios = build_portfolio(general_scores, top_pct=0.25, bottom_pct=0.25)
    general_returns = compute_returns(general_portfolios)
    general_stats = performance_stats(general_returns)

    # Display side-by-side terminal comparison
    print("\n===========================================================")
    print("                QUANTAMENTAL BACKTEST COMPARISON           ")
    print("===========================================================")
    print(f"  Metric                  Permian E&P        General Corporate")
    print(f"  ---------------------------------------------------------")
    metrics_to_print = ["ann_return", "ann_vol", "sharpe", "max_drawdown", "hit_rate", "n_quarters"]
    for m in metrics_to_print:
        val_ep = stats.get(m)
        val_gc = general_stats.get(m)
        
        # Format string
        if m in ["ann_return", "ann_vol", "max_drawdown", "hit_rate"]:
            str_ep = f"{val_ep:.1%}" if val_ep is not None else "N/A"
            str_gc = f"{val_gc:.1%}" if val_gc is not None else "N/A"
        elif m == "sharpe":
            str_ep = f"{val_ep:.3f}" if val_ep is not None else "N/A"
            str_gc = f"{val_gc:.3f}" if val_gc is not None else "N/A"
        else:
            str_ep = str(val_ep)
            str_gc = str(val_gc)
            
        label = m.replace("_", " ").title()
        print(f"  {label:<24} {str_ep:<18} {str_gc}")
    print("===========================================================")

    # Save parquets
    returns.to_parquet(DATA_DIR / "scores" / "backtest_returns.parquet")
    general_returns.to_parquet(DATA_DIR / "scores" / "general_backtest_returns.parquet")
    print(f"\nWrote returns to parquet archives.")
    print(f"Done. Ready for dynamic front-end rendering!")


if __name__ == "__main__":
    main()
