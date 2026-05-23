"""Automated Tests for the Quantamental Narrative Engine."""
import pytest
import os
from src.narrative.generator import (
    get_general_narratives,
    get_ep_deterministic_fallback,
    get_ep_gemini_narratives
)

@pytest.fixture
def mock_general_data():
    return {
        "ticker": "TSLA",
        "name": "Tesla, Inc.",
        "sector": "Consumer Cyclical",
        "industry": "Auto Manufacturers",
        "tier": "C",
        "caligula_score": 0.476,
        "unit_economics_score": 0.174,
        "capital_discipline_score": 0.152,
        "balance_sheet_score": 0.835,
        "hedge_book_score": 0.862,
        "reserves_score": 0.523,
        "operational_score": 0.162,
        "sentiment_score": 0.970,
        "macro_sensitivity_score": 0.285,
        "raw_metrics": {
            "gross_margin": 0.19,
            "operating_margin": 0.04,
            "roa": 0.02,
            "fcf_yield": 0.003,
            "debt_ebitda": 1.43,
            "current_ratio": 2.04,
            "quick_ratio": 1.43,
            "cash_debt": 2.81,
            "revenue_growth": 0.158,
            "earnings_growth": 0.083,
            "roe": 0.049,
            "peg_ratio": 5.87,
            "short_pct": 0.023,
            "short_ratio": 1.13,
            "beta": 1.79
        }
    }

@pytest.fixture
def mock_ep_data():
    return {
        "ticker": "FANG",
        "name": "Diamondback Energy, Inc.",
        "sector": "Energy",
        "industry": "Oil & Gas Exploration & Production",
        "tier": "A",
        "caligula_score": 0.812,
        "unit_economics_score": 0.84,
        "capital_discipline_score": 0.79,
        "balance_sheet_score": 0.88,
        "hedge_book_score": 0.74,
        "reserves_score": 0.85,
        "operational_score": 0.77,
        "sentiment_score": 0.81,
        "macro_sensitivity_score": 0.82
    }

def test_general_narratives_structure(mock_general_data):
    """Verify that general narratives yield correct structural dictionary keys."""
    res = get_general_narratives(mock_general_data)
    
    required_keys = [
        "summary", "unit_economics_score", "capital_discipline_score", "balance_sheet_score",
        "hedge_book_score", "reserves_score", "operational_score", "sentiment_score", "macro_sensitivity_score"
    ]
    
    for key in required_keys:
        assert key in res
        assert isinstance(res[key], str)
        assert len(res[key]) > 10

def test_general_narratives_compliance(mock_general_data):
    """Verify that general narratives are objective, contain exact percentages and no opinions."""
    res = get_general_narratives(mock_general_data)
    
    # Assert factual metric presence
    assert "19.0%" in res["unit_economics_score"]
    assert "4.0%" in res["unit_economics_score"]
    assert "1.43x" in res["balance_sheet_score"]
    
    # Assert academic, objective framing
    assert "buy" not in res["summary"].lower()
    assert "sell" not in res["summary"].lower()
    assert "should" not in res["summary"].lower()

def test_ep_deterministic_fallback(mock_ep_data):
    """Verify that the E&P deterministic fallback generates specialized Delaware Basin geology narratives."""
    res = get_ep_deterministic_fallback(mock_ep_data)
    
    required_keys = [
        "summary", "unit_economics_score", "capital_discipline_score", "balance_sheet_score",
        "hedge_book_score", "reserves_score", "operational_score", "sentiment_score", "macro_sensitivity_score"
    ]
    
    for key in required_keys:
        assert key in res
        assert isinstance(res[key], str)
        
    assert "Delaware Basin" in res["summary"]
    assert "horizontal drilling" in res["unit_economics_score"]

def test_ep_gemini_fallback_without_key(mock_ep_data):
    """Assert that the Gemini client gracefully falls back to deterministic matrices when API key is absent."""
    # Temporarily remove key if present
    old_key = os.environ.pop("GEMINI_API_KEY", None)
    
    try:
        res = get_ep_gemini_narratives(mock_ep_data)
        assert "Delaware Basin" in res["summary"]
        assert isinstance(res["balance_sheet_score"], str)
    finally:
        if old_key:
            os.environ["GEMINI_API_KEY"] = old_key
