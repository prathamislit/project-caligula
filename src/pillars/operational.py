"""Pillar 6: Operational Momentum."""
import pandas as pd


def prod_growth_debt_adj_share(llm_data: dict):
    """Annual organic production growth rate. Higher is better."""
    if not llm_data:
        return None
    prod = llm_data.get("production_mmboe", 0) or 0
    additions = llm_data.get("organic_additions_mmboe", 0) or 0
    if prod == 0:
        return None
    # Organic expansion rate
    return float(additions / prod)


def well_productivity_trend(llm_data: dict):
    """Acreage geologic tier well productivity factor. Higher represents superior quality acreage."""
    if not llm_data:
        return None
    breakeven = llm_data.get("breakeven_wti_10pct", 50.0) or 50.0
    # Lower breakeven = higher productivity acreage
    if breakeven == 0:
        return None
    return float(60.0 / breakeven - 1.0)


def rig_count_trajectory(llm_data: dict):
    """Rig activity pacing multiplier. Higher represents rising interest."""
    if not llm_data:
        return None
    proved = llm_data.get("total_proved_mmboe", 0) or 0
    developed = llm_data.get("proved_developed_mmboe", 0) or 0
    pud = proved - developed
    if developed == 0 or pud <= 0:
        return 0.2  # Base pace
    # Ratio of unproved/developed represents structural development pipeline
    return float(pud / developed)


def all_operational_metrics(llm_data: dict) -> dict:
    return {
        "prod_growth_debt_adj_share": prod_growth_debt_adj_share(llm_data),
        "well_productivity_trend": well_productivity_trend(llm_data),
        "rig_count_trajectory": rig_count_trajectory(llm_data),
    }
