"""Pillar 4: Hedge Book Quality."""
import pandas as pd
from ..ingest.fred_client import get_series


def _get_wti_spot(as_of: pd.Timestamp):
    """Fetch point-in-time WTI spot price as strip proxy."""
    wti = get_series("DCOILWTICO")
    if wti is None or wti.empty:
        return 75.0  # Conservative commodity price fallback
    wti = wti.copy()
    wti["date"] = pd.to_datetime(wti["date"])
    wti = wti[wti["date"] <= as_of].sort_values("date")
    if wti.empty:
        return 75.0
    return float(wti["DCOILWTICO"].iloc[-1])


def pct_oil_hedged_ntm(llm_data: dict):
    """% of next-12-month production hedged. Higher is better for downside protection."""
    if not llm_data or "pct_oil_hedged_ntm" not in llm_data:
        return None
    return float(llm_data["pct_oil_hedged_ntm"])


def hedge_floor_vs_strip(llm_data: dict, as_of: pd.Timestamp):
    """Locked-in floor price relative to WTI spot at quarter-end."""
    if not llm_data or "weighted_floor" not in llm_data:
        return None
    floor = llm_data["weighted_floor"]
    strip = _get_wti_spot(as_of)
    if not strip or strip == 0:
        return None
    return float(floor / strip)


def hedge_instrument_quality(llm_data: dict):
    """Derivative structure score: Swap (1.0) -> Put (0.8) -> Collar (0.6)."""
    if not llm_data:
        return None
    swap = llm_data.get("swap_pct", 0.0) or 0.0
    put = llm_data.get("put_pct", 0.0) or 0.0
    collar = llm_data.get("collar_pct", 0.0) or 0.0
    
    total = swap + put + collar
    if total == 0:
        return 0.5  # Neutral fallback
    
    # Weighted quality
    score = (swap * 1.0 + put * 0.8 + collar * 0.6) / total
    return float(score)


def all_hedge_book_metrics(llm_data: dict, as_of: pd.Timestamp) -> dict:
    return {
        "pct_oil_hedged_ntm": pct_oil_hedged_ntm(llm_data),
        "hedge_floor_vs_strip": hedge_floor_vs_strip(llm_data, as_of),
        "hedge_instrument_quality": hedge_instrument_quality(llm_data),
    }
