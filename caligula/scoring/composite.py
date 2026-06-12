"""Calculate composite scores from pillar inputs."""

import warnings

import pandas as pd
from caligula.errors import CaligulaScoringError
from caligula.scoring.pillars import compute_all_pillars, load_methodology

_EQUAL_WEIGHTS = {
    "hedge_book_score": 0.125,
    "reserves_score": 0.125,
    "unit_economics_score": 0.125,
    "balance_sheet_score": 0.125,
    "capital_discipline_score": 0.125,
    "operational_score": 0.125,
    "sentiment_score": 0.125,
    "macro_sensitivity_score": 0.125,
}


def _load_pillar_weights(methodology: dict) -> dict:
    """Build {pillar_column: weight} from the canonical weights.yaml.

    weights.yaml defines pillars under `pillars:` keyed by short name
    (e.g. `unit_economics: {weight: 18, ...}`); pillar columns are
    `<short_name>_score`. Weights are normalized to sum to 1.0.
    """
    pillars = methodology.get("pillars") or {}
    weights = {
        f"{name}_score": float(spec["weight"])
        for name, spec in pillars.items()
        if isinstance(spec, dict) and "weight" in spec
    }
    total = sum(weights.values())
    if not weights or total <= 0:
        warnings.warn(
            "weights.yaml has no usable `pillars:` weights — "
            "falling back to equal pillar weights.",
            stacklevel=2,
        )
        return dict(_EQUAL_WEIGHTS)
    return {k: w / total for k, w in weights.items()}


def _assign_tiers_absolute(scores: pd.Series, tier_bands: dict) -> pd.Series:
    """Assign tiers from absolute score bands defined in weights.yaml
    (e.g. A: [0.70, 1.00]). Bands are evaluated by descending lower bound."""
    bands = sorted(
        ((tier, float(bounds[0])) for tier, bounds in tier_bands.items()),
        key=lambda item: item[1],
        reverse=True,
    )
    lowest_tier = bands[-1][0]

    def tier_for(score: float) -> str:
        for tier, lo in bands:
            if score >= lo:
                return tier
        return lowest_tier

    return scores.apply(tier_for)


def compute_composite(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate composite score and assign tiers."""
    pillars_df = compute_all_pillars(df)
    methodology = load_methodology()
    weights = _load_pillar_weights(methodology)

    composite = pd.Series(0.0, index=pillars_df.index)
    for pillar, weight in weights.items():
        if pillar in pillars_df.columns:
            composite += pillars_df[pillar] * weight

    if composite.isna().any():
        bad = pillars_df.loc[composite.isna(), "ticker"].tolist()
        raise CaligulaScoringError(
            f"NaN composite score for {bad} — a pillar input is null. "
            "Refusing to rank on missing data."
        )

    pillars_df["caligula_score"] = composite

    # Calculate cross-sectional rank (1 = highest score)
    # Using 'min' to handle ties (e.g. 1, 2, 2, 4)
    pillars_df["rank"] = pillars_df["caligula_score"].rank(
        ascending=False, method="min"
    )

    # Assign tiers from the absolute bands in weights.yaml; fall back to
    # rank quantiles only if no bands are configured.
    tier_bands = methodology.get("tiers") or {}
    if tier_bands:
        pillars_df["tier"] = _assign_tiers_absolute(
            pillars_df["caligula_score"], tier_bands
        )
    else:

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
