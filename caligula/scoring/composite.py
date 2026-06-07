"""Calculate composite scores from pillar inputs."""

import pandas as pd
from caligula.scoring.pillars import compute_all_pillars, load_methodology


def compute_composite(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate composite score and assign tiers."""
    pillars_df = compute_all_pillars(df)

    weights = load_methodology().get(
        "pillar_weights",
        {
            "hedge_book_score": 0.125,
            "reserves_score": 0.125,
            "unit_economics_score": 0.125,
            "balance_sheet_score": 0.125,
            "capital_discipline_score": 0.125,
            "operational_score": 0.125,
            "sentiment_score": 0.125,
            "macro_sensitivity_score": 0.125,
        },
    )

    composite = pd.Series(0.0, index=pillars_df.index)

    for pillar, weight in weights.items():
        if pillar in pillars_df.columns:
            composite += pillars_df[pillar] * weight

    pillars_df["caligula_score"] = composite

    # Calculate cross-sectional rank (1 = highest score)
    # Using 'min' to handle ties (e.g. 1, 2, 2, 4)
    pillars_df["rank"] = pillars_df["caligula_score"].rank(
        ascending=False, method="min"
    )

    # Assign Tiers based on rank quantiles
    def assign_tier(r, max_r):
        q = r / max_r
        if q <= 0.25:
            return "A"
        if q <= 0.50:
            return "B"
        if q <= 0.75:
            return "C"
        return "D"

    max_rank = pillars_df["rank"].max()
    if max_rank > 0:
        pillars_df["tier"] = pillars_df["rank"].apply(
            lambda r: assign_tier(r, max_rank)
        )
    else:
        pillars_df["tier"] = "C"

    return pillars_df
