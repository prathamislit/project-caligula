"""Composite Caligula Score — 8-pillar weighted composite."""
import pandas as pd
import numpy as np
from ..utils.config import load_weights
from .normalize import normalize_metric


def compute_pillar_score(df: pd.DataFrame, pillar: str, weights_config: dict) -> pd.Series:
    pillar_cfg = weights_config["pillars"][pillar]
    metric_direction = weights_config["metric_direction"]
    metrics = pillar_cfg["metrics"]

    weighted_sum = pd.Series(0.0, index=df.index)
    coverage = pd.Series(0.0, index=df.index)

    for metric, mw in metrics.items():
        if metric not in df.columns:
            continue
        direction = metric_direction.get(metric, 1)
        normalized = normalize_metric(df, metric, direction)
        present = normalized.notna()
        weighted_sum = weighted_sum.add(normalized.fillna(0) * mw, fill_value=0)
        coverage = coverage.add(present.astype(float) * mw, fill_value=0)

    coverage_safe = coverage.where(coverage > 0, np.nan)
    pillar_score = weighted_sum / coverage_safe
    return pd.Series(pillar_score, index=df.index)


def compute_composite(df: pd.DataFrame) -> pd.DataFrame:
    weights = load_weights()
    pillars = weights["pillars"]

    result = df[["ticker"]].copy() if "ticker" in df.columns else pd.DataFrame(index=df.index)
    composite = pd.Series(0.0, index=df.index)
    pillar_coverage = pd.Series(0.0, index=df.index)

    for pillar_name, pillar_cfg in pillars.items():
        p_score = compute_pillar_score(df, pillar_name, weights)
        result[f"{pillar_name}_score"] = p_score
        present = p_score.notna()
        composite = composite.add(p_score.fillna(0) * pillar_cfg["weight"], fill_value=0)
        pillar_coverage = pillar_coverage.add(
            present.astype(float) * pillar_cfg["weight"], fill_value=0
        )

    total_weight = sum(c["weight"] for c in pillars.values())
    result["caligula_score"] = np.where(
        pillar_coverage > 0, composite / total_weight, np.nan
    )
    score_cols = [c for c in result.columns if c.endswith("_score")]
    result[score_cols] = result[score_cols].astype(float)
    result["tier"] = assign_tier(result["caligula_score"], weights["tiers"])
    return result


def assign_tier(scores: pd.Series, tier_bounds: dict) -> pd.Series:
    def to_tier(s):
        if pd.isna(s):
            return None
        for label, bounds in tier_bounds.items():
            lo, hi = bounds[0], bounds[1]
            if lo <= s <= hi:
                return label
        return None
    return scores.apply(to_tier)
