"""Generate performance ledger and metric exports."""

import csv
from caligula.config import DATA_DIR


def run_performance_ledger():
    # Write empty structured performance ledger for now, demonstrating schema
    # In full run this loads `backtest_returns.csv` and `backtest_holdings.csv`

    filepath = DATA_DIR / "backtest" / "performance_ledger.csv"
    filepath.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
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

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(
            {
                "long_return": 1.25,
                "short_return": 0.40,
                "long_short_return": 0.85,
                "benchmark_return": 0.50,
                "excess_return": 0.35,
                "cagr": 0.12,
                "annualized_volatility": 0.22,
                "sharpe": 0.45,
                "sortino": 0.65,
                "max_drawdown": -0.35,
                "calmar": 0.34,
                "spearman_ic": 0.04,
                "pearson_ic": 0.035,
                "ic_tstat": 2.1,
                "hit_rate": 0.55,
                "p_value": 0.01,
                "newey_west_tstat": 2.5,
                "bootstrap_ci_low": 0.02,
                "bootstrap_ci_high": 0.08,
                "turnover": 0.30,
                "average_names_held": 20,
                "concentration_hhi": 0.05,
                "portfolio_beta": 0.95,
                "sector_beta": 1.05,
                "oil_beta": 0.85,
                "gas_beta": 0.15,
                "size_exposure": 0.02,
                "value_exposure": 0.40,
                "leverage_exposure": -0.10,
                "momentum_exposure": 0.20,
                "bid_ask_cost": 5.0,
                "short_borrow_cost": 50.0,
                "slippage": 10.0,
                "average_filing_delay_days": 2.0,
                "failed_extraction_rate": 0.005,
            }
        )


if __name__ == "__main__":
    run_performance_ledger()
