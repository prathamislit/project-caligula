"""Tests for scoring pipeline."""
import pandas as pd
import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.scoring.normalize import percentile_rank, winsorize, normalize_metric
from src.scoring.composite import compute_composite, assign_tier


class TestNormalize:
    def test_percentile_rank_ascending(self):
        s = pd.Series([1.0, 2.0, 3.0, 4.0])
        r = percentile_rank(s, direction=1)
        assert r.iloc[-1] > r.iloc[0]
        assert r.max() <= 1.0
        assert r.min() >= 0.0

    def test_percentile_rank_descending(self):
        s = pd.Series([1.0, 2.0, 3.0, 4.0])
        r = percentile_rank(s, direction=-1)
        assert r.iloc[0] > r.iloc[-1]

    def test_winsorize_clips_extremes(self):
        s = pd.Series([0.0] + list(range(1, 99)) + [10000.0])
        w = winsorize(s)
        assert w.max() < 10000.0

    def test_normalize_metric_with_nans(self):
        df = pd.DataFrame({
            "ticker": ["A", "B", "C", "D"],
            "fcf_yield_ttm": [0.05, 0.10, np.nan, 0.03],
        })
        result = normalize_metric(df, "fcf_yield_ttm", direction=1)
        assert result.notna().sum() == 3
        assert result.max() <= 1.0


class TestComposite:
    def _make_df(self):
        rng = np.random.default_rng(0)
        tickers = ["FANG", "PXD", "MTDR", "EOG", "SM", "CTRA"]
        data = {"ticker": tickers}
        # Sprinkle some metric columns that exist in weights.yaml
        for col in ["fcf_yield_ttm", "capital_return_yield", "net_debt_to_ebitdax",
                    "realized_vol_relative", "drawdown_recovery_halflife"]:
            data[col] = rng.uniform(0, 1, len(tickers))
        return pd.DataFrame(data)

    def test_composite_returns_score_column(self):
        df = self._make_df()
        result = compute_composite(df)
        assert "caligula_score" in result.columns

    def test_composite_scores_in_range(self):
        df = self._make_df()
        result = compute_composite(df)
        valid = result["caligula_score"].dropna()
        assert (valid >= 0).all() and (valid <= 1).all()

    def test_tier_assignment(self):
        scores = pd.Series([0.80, 0.60, 0.40, 0.20])
        from src.utils.config import load_weights
        tiers = load_weights()["tiers"]
        result = assign_tier(scores, tiers)
        assert result.iloc[0] == "A"
        assert result.iloc[1] == "B"
        assert result.iloc[2] == "C"
        assert result.iloc[3] == "D"

    def test_composite_handles_all_nan_pillar(self):
        df = pd.DataFrame({"ticker": ["X", "Y"]})
        result = compute_composite(df)
        assert "caligula_score" in result.columns


class TestUniverseReconstructor:
    def test_active_universe_at_2020(self):
        from src.backtest.universe_reconstructor import active_universe_at
        active = active_universe_at(pd.Timestamp("2020-06-30"))
        tickers = [c["ticker"] for c in active]
        assert "FANG" in tickers
        assert "EOG" in tickers

    def test_acquired_company_not_active_after_end(self):
        from src.backtest.universe_reconstructor import active_universe_at
        # PXD acquired May 2024 — should not appear after that
        active = active_universe_at(pd.Timestamp("2025-01-01"))
        tickers = [c["ticker"] for c in active]
        assert "PXD" not in tickers

    def test_quarter_universe_table_shape(self):
        from src.backtest.universe_reconstructor import quarter_universe_table
        df = quarter_universe_table("2020-01-01", "2020-12-31")
        assert len(df) > 0
        assert "ticker" in df.columns
        assert "quarter" in df.columns


class TestMacroSensitivity:
    def test_downside_beta(self):
        from src.pillars.macro_sensitivity import downside_beta_wti
        beta = downside_beta_wti("FANG", pd.Timestamp("2025-03-31"))
        assert beta is not None
        assert isinstance(beta, float)

    def test_drawdown_recovery_halflife(self):
        from src.pillars.macro_sensitivity import drawdown_recovery_halflife
        hl = drawdown_recovery_halflife("FANG", pd.Timestamp("2025-03-31"))
        assert hl is not None
        assert isinstance(hl, float)
