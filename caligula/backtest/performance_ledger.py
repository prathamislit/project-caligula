"""Generate performance ledger from the real backtest return series.

Reads data/scores/backtest_returns.parquet (produced by run_backtest.py)
and the cached benchmark prices, and writes the canonical performance
ledger. Fields that cannot be computed from available data are left blank
rather than filled with placeholder values.
"""

import csv

import numpy as np
import pandas as pd

from caligula.config import (
    DATA_DIR,
    SHORT_BORROW_BPS,
    TRANSACTION_COST_BPS,
)

FIELDNAMES = [
    "long_return",
    "short_return",
    "long_short_return",
    "benchmark_return",
    "excess_return",
    "cagr",
    "annualized_volatility",
    "sharpe",
    "sortino",
    "max_drawdown",
    "calmar",
    "spearman_ic",
    "pearson_ic",
    "ic_tstat",
    "hit_rate",
    "p_value",
    "newey_west_tstat",
    "bootstrap_ci_low",
    "bootstrap_ci_high",
    "turnover",
    "average_names_held",
    "concentration_hhi",
    "portfolio_beta",
    "sector_beta",
    "oil_beta",
    "gas_beta",
    "size_exposure",
    "value_exposure",
    "leverage_exposure",
    "momentum_exposure",
    "bid_ask_cost",
    "short_borrow_cost",
    "slippage",
    "average_filing_delay_days",
    "failed_extraction_rate",
]

RETURNS_PATH = DATA_DIR / "scores" / "backtest_returns.parquet"


def _benchmark_quarterly_returns(ticker: str, quarters: pd.Series):
    """Quarterly holding returns for a benchmark, from the cached price store."""
    from src.ingest.price_client import get_prices

    px = get_prices(ticker)
    if px is None or px.empty:
        return None
    px = px.copy()
    px["date"] = pd.to_datetime(px["date"])
    px = px.sort_values("date")

    rets = []
    for q in quarters:
        start = pd.Timestamp(q)
        end = start + pd.Timedelta(days=91)
        s = px[px["date"] >= start]["close"].head(1)
        e = px[px["date"] >= end]["close"].head(1)
        rets.append(
            float(e.iloc[0] / s.iloc[0] - 1) if not s.empty and not e.empty else np.nan
        )
    return pd.Series(rets, index=quarters.values)


def _beta(port: pd.Series, bench: pd.Series):
    df = pd.concat([port, bench], axis=1).dropna()
    if len(df) < 8 or df.iloc[:, 1].var() == 0:
        return None
    return float(df.iloc[:, 0].cov(df.iloc[:, 1]) / df.iloc[:, 1].var())


def _fmt(v, decimals=6):
    return "" if v is None or (isinstance(v, float) and np.isnan(v)) else round(v, decimals)


def run_performance_ledger():
    filepath = DATA_DIR / "backtest" / "performance_ledger.csv"
    filepath.parent.mkdir(parents=True, exist_ok=True)

    row = {k: "" for k in FIELDNAMES}

    if RETURNS_PATH.exists():
        r = pd.read_parquet(RETURNS_PATH).sort_values("quarter").reset_index(drop=True)
        ls = r["ls_return"]
        n = len(ls)

        row["long_return"] = _fmt(float((1 + r["long_return"]).prod() - 1))
        row["short_return"] = _fmt(float((1 + r["short_return"]).prod() - 1))
        row["long_short_return"] = _fmt(float((1 + ls).prod() - 1))

        years = n / 4.0
        cum = float((1 + ls).prod())
        cagr = cum ** (1 / years) - 1 if years > 0 and cum > 0 else None
        row["cagr"] = _fmt(cagr)

        vol = float(ls.std() * np.sqrt(4))
        row["annualized_volatility"] = _fmt(vol)
        ann_ret = (1 + ls.mean()) ** 4 - 1
        row["sharpe"] = _fmt(ann_ret / vol) if vol > 0 else ""
        downside = ls[ls < 0]
        dvol = float(downside.std() * np.sqrt(4)) if len(downside) > 1 else None
        row["sortino"] = _fmt(ann_ret / dvol) if dvol else ""

        curve = (1 + ls).cumprod()
        max_dd = float((curve / curve.cummax() - 1).min())
        row["max_drawdown"] = _fmt(max_dd)
        row["calmar"] = _fmt(cagr / abs(max_dd)) if cagr is not None and max_dd < 0 else ""
        row["hit_rate"] = _fmt(float((ls > 0).mean()))

        # t-test of mean quarterly L/S return vs zero
        if n > 2 and ls.std() > 0:
            tstat = float(ls.mean() / (ls.std() / np.sqrt(n)))
            from scipy import stats as _st

            row["p_value"] = _fmt(float(2 * (1 - _st.t.cdf(abs(tstat), df=n - 1))))
            row["ic_tstat"] = ""

        # Bootstrap CI on mean quarterly L/S return
        rng = np.random.default_rng(42)
        boots = [
            float(rng.choice(ls.values, size=n, replace=True).mean())
            for _ in range(2000)
        ]
        row["bootstrap_ci_low"] = _fmt(float(np.percentile(boots, 2.5)))
        row["bootstrap_ci_high"] = _fmt(float(np.percentile(boots, 97.5)))

        row["average_names_held"] = _fmt(float((r["n_long"] + r["n_short"]).mean()), 2)
        # Equal-weight HHI per quarter: sum of squared weights
        hhi = (1.0 / r["n_long"] + 1.0 / r["n_short"]) / 4.0  # gross weight 0.5 long / 0.5 short
        row["concentration_hhi"] = _fmt(float(hhi.mean()))

        # Benchmark + betas from cached prices (skip silently if cache missing)
        try:
            quarters = r["quarter"]
            xop = _benchmark_quarterly_returns("XOP", quarters)
            spy = _benchmark_quarterly_returns("SPY", quarters)
            wti = _benchmark_quarterly_returns("CL=F", quarters)
            ls_idx = pd.Series(ls.values, index=quarters.values)
            if xop is not None:
                xop_clean = xop.dropna()
                row["benchmark_return"] = _fmt(float((1 + xop_clean).prod() - 1))
                if row["long_short_return"] != "" and row["benchmark_return"] != "":
                    row["excess_return"] = _fmt(
                        row["long_short_return"] - row["benchmark_return"]
                    )
                row["sector_beta"] = _fmt(_beta(ls_idx, xop), 4)
            if spy is not None:
                row["portfolio_beta"] = _fmt(_beta(ls_idx, spy), 4)
            if wti is not None:
                row["oil_beta"] = _fmt(_beta(ls_idx, wti), 4)
        except Exception:
            pass

        # Cost assumptions from canonical config (bps)
        row["bid_ask_cost"] = TRANSACTION_COST_BPS
        row["short_borrow_cost"] = SHORT_BORROW_BPS

        # Extraction failure rate from the real score panel
        panel_path = DATA_DIR / "scores" / "all_scores.parquet"
        if panel_path.exists():
            panel = pd.read_parquet(panel_path)
            if "caligula_score" in panel.columns and len(panel):
                row["failed_extraction_rate"] = _fmt(
                    float(panel["caligula_score"].isna().mean())
                )

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerow(row)

    return filepath


if __name__ == "__main__":
    run_performance_ledger()
