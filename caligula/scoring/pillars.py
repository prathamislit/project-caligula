"""Canonical factor calculations for the Caligula scoring engine."""

import pandas as pd
import yaml
from caligula.config import ROOT


def load_methodology() -> dict:
    with open(ROOT / "config" / "weights.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def calculate_hedge_book_score(df: pd.DataFrame) -> pd.Series:
    """Example pillar calculation: Hedge Book."""
    if "pct_oil_hedged_ntm" not in df.columns or "weighted_floor" not in df.columns:
        return pd.Series(0.5, index=df.index)

    # Simple metric: coverage * floor
    raw = df["pct_oil_hedged_ntm"] * df["weighted_floor"]

    # Normalize 0 to 1
    if raw.max() == raw.min():
        return pd.Series(0.5, index=df.index)
    return (raw - raw.min()) / (raw.max() - raw.min())


def calculate_reserve_score(df: pd.DataFrame) -> pd.Series:
    """Example pillar calculation: Reserves."""
    if "tier1_years" not in df.columns:
        return pd.Series(0.5, index=df.index)

    raw = df["tier1_years"]
    if raw.max() == raw.min():
        return pd.Series(0.5, index=df.index)
    return (raw - raw.min()) / (raw.max() - raw.min())


def calculate_unit_economics_score(df: pd.DataFrame) -> pd.Series:
    """Example pillar calculation: Unit Economics."""
    if "fd_cost_per_boe" not in df.columns or "cash_opex_per_boe" not in df.columns:
        return pd.Series(0.5, index=df.index)

    # Lower cost is better
    raw = -(df["fd_cost_per_boe"] + df["cash_opex_per_boe"])
    if raw.max() == raw.min():
        return pd.Series(0.5, index=df.index)
    return (raw - raw.min()) / (raw.max() - raw.min())


def compute_all_pillars(df: pd.DataFrame) -> pd.DataFrame:
    """Computes all pillars based on available raw metrics in the dataframe."""
    out = pd.DataFrame(index=df.index)
    out["ticker"] = df["ticker"]
    out["quarter"] = df["quarter"]
    out["hedge_book_score"] = calculate_hedge_book_score(df)
    out["reserves_score"] = calculate_reserve_score(df)
    out["unit_economics_score"] = calculate_unit_economics_score(df)

    # Fill remaining pillars with neutral 0.5 if not available yet
    for p in [
        "balance_sheet_score",
        "capital_discipline_score",
        "operational_score",
        "sentiment_score",
        "macro_sensitivity_score",
    ]:
        if p not in out.columns:
            out[p] = 0.5

    return out
