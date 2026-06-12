"""v2: End-to-end backtest runner.

Usage:
    python run_backtest.py             # reuse cached score panels if present
    python run_backtest.py --refresh   # force full re-scoring (EDGAR + LLM)
"""
import argparse
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
from src.utils.config import load_universe, DATA_DIR
from src.ingest.price_client import get_prices
from src.backtest.score_history import run_backtest_scoring, run_general_backtest_scoring
from src.backtest.portfolio_engine import build_portfolio, compute_returns, performance_stats

SCORES_DIR = DATA_DIR / "scores"


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


def load_or_compute_scores(refresh: bool):
    """Load the cached score panel unless a refresh is requested."""
    path = SCORES_DIR / "all_scores.parquet"
    if not refresh and path.exists():
        scores = pd.read_parquet(path)
        print(f"Loaded cached Permian score panel: {len(scores)} rows "
              f"({scores['quarter'].nunique()} quarters). Use --refresh to recompute.")
        return scores
    print("\nRunning quarterly Permian E&P backtest scoring...")
    return run_backtest_scoring()


def load_or_compute_general_scores(refresh: bool):
    path = SCORES_DIR / "general_scores.parquet"
    if not refresh and path.exists():
        scores = pd.read_parquet(path)
        print(f"Loaded cached General Corporate score panel: {len(scores)} rows. "
              "(NOTE: simulated comparison universe, not real fundamentals.)")
        return scores
    print("\nRunning quarterly General Corporate backtest scoring (simulated comparison)...")
    return run_general_backtest_scoring()


def main():
    parser = argparse.ArgumentParser(description="Caligula end-to-end backtest")
    parser.add_argument("--refresh", action="store_true",
                        help="Force full re-scoring instead of reusing cached panels")
    args = parser.parse_args()

    ensure_prices_cached()

    scores = load_or_compute_scores(args.refresh)
    general_scores = load_or_compute_general_scores(args.refresh)

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
    print(f"  Metric                  Permian E&P        General Corporate*")
    print(f"  ---------------------------------------------------------")
    metrics_to_print = ["ann_return", "ann_vol", "sharpe", "max_drawdown", "hit_rate", "n_quarters"]
    for m in metrics_to_print:
        val_ep = stats.get(m)
        val_gc = general_stats.get(m)

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
    print("  * General Corporate scores are a simulated comparison universe.")
    print("===========================================================")

    # Save parquets
    returns.to_parquet(SCORES_DIR / "backtest_returns.parquet")
    general_returns.to_parquet(SCORES_DIR / "general_backtest_returns.parquet")
    print(f"\nWrote returns to parquet archives.")

    # Regenerate the canonical performance ledger from the real return series
    from caligula.backtest.performance_ledger import run_performance_ledger
    run_performance_ledger()
    print("Regenerated data/backtest/performance_ledger.csv from real returns.")


if __name__ == "__main__":
    main()
