"""Pillar 1: Unit Economics."""
import pandas as pd


def fd_cost_per_boe_3yr(llm_data: dict):
    """3-year Finding and Development cost per BOE. Lower is better."""
    if not llm_data or "fd_cost_per_boe" not in llm_data:
        return None
    return float(llm_data["fd_cost_per_boe"])


def cash_opex_per_boe(llm_data: dict):
    """Cash lease operating expenses (LOE) + taxes per BOE. Lower is better."""
    if not llm_data or "cash_opex_per_boe" not in llm_data:
        return None
    return float(llm_data["cash_opex_per_boe"])


def breakeven_wti_10pct_irr(llm_data: dict):
    """WTI crude oil price needed to earn a 10% IRR on average wells. Lower is better."""
    if not llm_data or "breakeven_wti_10pct" not in llm_data:
        return None
    return float(llm_data["breakeven_wti_10pct"])


def recycle_ratio(llm_data: dict):
    """Recycle Ratio = cash opex per boe / F&D cost per boe. Higher is better."""
    if not llm_data:
        return None
    fd = llm_data.get("fd_cost_per_boe")
    cash_margin = llm_data.get("cash_opex_per_boe")  # Margin proxy for relative scoring
    if not fd or not cash_margin or fd == 0:
        return None
    # Standard: (Avg Price - LOE) / F&D cost. We score cash opex and LOE discipline
    return float(cash_margin / fd)


def all_unit_economics_metrics(llm_data: dict) -> dict:
    return {
        "fd_cost_per_boe_3yr": fd_cost_per_boe_3yr(llm_data),
        "cash_opex_per_boe": cash_opex_per_boe(llm_data),
        "breakeven_wti_10pct_irr": breakeven_wti_10pct_irr(llm_data),
        "recycle_ratio": recycle_ratio(llm_data),
    }
