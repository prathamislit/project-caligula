"""Performance and portfolio metrics for the backtest engine."""

import numpy as np
import pandas as pd
from scipy import stats


def calc_cagr(returns: pd.Series, periods_per_year: int = 4) -> float:
    """Annualized geometric return."""
    if len(returns) == 0:
        return 0.0
    cum_ret = (1 + returns).prod()
    years = len(returns) / periods_per_year
    return float(cum_ret ** (1 / years) - 1)


def calc_annualized_volatility(returns: pd.Series, periods_per_year: int = 4) -> float:
    """Standard deviation of periodic returns annualized."""
    return float(returns.std() * np.sqrt(periods_per_year))


def calc_sharpe(
    returns: pd.Series, risk_free_rate: float = 0.02, periods_per_year: int = 4
) -> float:
    """Annualized excess return divided by annualized volatility."""
    vol = calc_annualized_volatility(returns, periods_per_year)
    if vol == 0:
        return 0.0
    cagr = calc_cagr(returns, periods_per_year)
    return float((cagr - risk_free_rate) / vol)


def calc_sortino(
    returns: pd.Series, risk_free_rate: float = 0.02, periods_per_year: int = 4
) -> float:
    """Annualized excess return divided by downside deviation."""
    cagr = calc_cagr(returns, periods_per_year)
    downside = returns[returns < 0]
    if len(downside) == 0:
        return float("inf")
    downside_dev = float(downside.std() * np.sqrt(periods_per_year))
    if downside_dev == 0:
        return 0.0
    return float((cagr - risk_free_rate) / downside_dev)


def calc_max_drawdown(returns: pd.Series) -> float:
    """Largest peak-to-trough decline."""
    cum_ret = (1 + returns).cumprod()
    peak = cum_ret.cummax()
    drawdown = (cum_ret - peak) / peak
    return float(drawdown.min())


def calc_calmar(cagr: float, max_drawdown: float) -> float:
    """CAGR divided by absolute max drawdown."""
    if max_drawdown == 0:
        return float("inf")
    return float(cagr / abs(max_drawdown))


def calc_spearman_ic(scores: pd.Series, forward_returns: pd.Series) -> float:
    """Rank correlation between signal score and forward return."""
    if len(scores) < 2:
        return 0.0
    return float(stats.spearmanr(scores, forward_returns).correlation)


def calc_pearson_ic(scores: pd.Series, forward_returns: pd.Series) -> float:
    """Linear correlation between signal score and forward return."""
    if len(scores) < 2:
        return 0.0
    return float(np.corrcoef(scores, forward_returns)[0, 1])


def calc_ic_tstat(ic_series: pd.Series) -> float:
    """Mean IC divided by standard error."""
    if len(ic_series) < 2:
        return 0.0
    se = ic_series.std() / np.sqrt(len(ic_series))
    if se == 0:
        return 0.0
    return float(ic_series.mean() / se)


def calc_hit_rate(long_returns: pd.Series, short_returns: pd.Series) -> float:
    """Share of periods where long book outperformed short book."""
    if len(long_returns) == 0:
        return 0.0
    hits = (long_returns > short_returns).sum()
    return float(hits / len(long_returns))


def calc_newey_west_tstat(return_series: pd.Series, lags: int = 4) -> float:
    """Autocorrelation-adjusted t-stat for return series."""
    # Simplified standard error for demonstration
    if len(return_series) < lags + 2:
        return 0.0
    return float(
        return_series.mean() / (return_series.std() / np.sqrt(len(return_series)))
    )


def calc_bootstrap_ci(
    return_series: pd.Series, n_bootstrap: int = 1000, ci: float = 0.95
) -> tuple:
    """Resampled return confidence interval."""
    if len(return_series) < 2:
        return (0.0, 0.0)
    samples = np.random.choice(
        return_series, (n_bootstrap, len(return_series)), replace=True
    )
    means = np.mean(samples, axis=1)
    lower = float(np.percentile(means, (1 - ci) / 2 * 100))
    upper = float(np.percentile(means, (1 + ci) / 2 * 100))
    return (lower, upper)


def calc_turnover(weights_by_period: pd.DataFrame) -> float:
    """Half the absolute change in portfolio weights."""
    if len(weights_by_period) < 2:
        return 0.0
    diffs = weights_by_period.fillna(0).diff().abs()
    return float(diffs.sum(axis=1).mean() / 2.0)


def calc_hhi(weights: pd.Series) -> float:
    """Sum of squared portfolio weights."""
    return float((weights**2).sum())


def calc_beta(strategy_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """Regression beta versus benchmark."""
    if len(strategy_returns) < 2:
        return 0.0
    cov = np.cov(strategy_returns, benchmark_returns)[0, 1]
    var = np.var(benchmark_returns)
    if var == 0:
        return 0.0
    return float(cov / var)
