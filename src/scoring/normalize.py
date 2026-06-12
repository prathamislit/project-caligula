"""Sector-normalized percentile ranking."""
import pandas as pd
import numpy as np


def percentile_rank(values: pd.Series, direction: int = 1) -> pd.Series:
    """0-1 percentile rank within universe.
    direction=1: higher raw value → higher score.
    direction=-1: lower raw value → higher score."""
    if values.isna().all():
        return values
    ranks = values.rank(pct=True, na_option="keep")
    if direction == -1:
        ranks = 1 - ranks
    return ranks


def winsorize(s: pd.Series, lower=0.05, upper=0.95) -> pd.Series:
    lo = s.quantile(lower)
    hi = s.quantile(upper)
    return s.clip(lo, hi)


def normalize_metric(df: pd.DataFrame, metric: str, direction: int) -> pd.Series:
    """Winsorize + percentile rank within universe cross-section."""
    if metric not in df.columns:
        return pd.Series(index=df.index, dtype=float)
    w = winsorize(df[metric])
    return percentile_rank(w, direction)
