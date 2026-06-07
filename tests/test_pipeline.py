"""Unit tests for the canonical Caligula pipeline."""

import ast
import csv
import json
from pathlib import Path

import pandas as pd

from caligula.backtest.audit_example import generate_audit_example
from caligula.backtest.performance_ledger import run_performance_ledger
from caligula.backtest.universe import generate_universe_ledger
from caligula.config import AUDIT_DIR, BACKTEST_DIR, DATA_DIR, ROOT, WEBSITE_DIR
from caligula.exports.website_public import export_website_json
from caligula.scoring.composite import compute_composite
from caligula.valuation.eog_dcf import run_eog_dcf
from caligula.valuation.reserve_tv import calculate_reserve_bucket_tv
from generate_proof_ledgers import populate_proof_ledgers


REQUIRED_COLUMNS = {
    AUDIT_DIR
    / "extraction_ledger.csv": [
        "ticker",
        "fiscal_year",
        "filing_type",
        "filing_accession",
        "filing_date",
        "accepted_datetime",
        "source_url",
        "source_table",
        "source_page",
        "source_text_hash",
        "raw_extracted_text",
        "field_name",
        "extracted_value",
        "unit",
        "prompt_version",
        "model_name",
        "confidence_score",
        "human_override_flag",
        "override_reason",
        "audit_hash",
        "created_at",
    ],
    DATA_DIR
    / "normalized"
    / "reserve_ledger.csv": [
        "ticker",
        "fiscal_year",
        "proved_developed",
        "proved_undeveloped",
        "total_proved",
        "oil_mmbbl",
        "gas_bcf",
        "ngl_mmbbl",
        "total_mmboe",
        "standardized_measure",
        "production_mmboe",
        "extensions_discoveries",
        "revisions",
        "purchases",
        "sales",
        "source_filing_accession",
        "audit_hash",
    ],
    BACKTEST_DIR
    / "universe_ledger.csv": [
        "rebalance_date",
        "ticker",
        "eligible_flag",
        "inclusion_reason",
        "exclusion_reason",
        "listing_status",
        "market_cap",
        "adv_30d",
        "filing_available_flag",
        "latest_filing_used",
        "latest_filing_date",
        "latest_filing_accepted_datetime",
        "sector",
        "basin",
        "delisting_return_applied",
    ],
    BACKTEST_DIR
    / "performance_ledger.csv": [
        "long_return",
        "short_return",
        "long_short_return",
        "benchmark_return",
        "excess_return",
        "cagr",
        "annualized_volatility",
        "sharpe",
        "sortino",
        "max_drawdown",
        "calmar",
        "spearman_ic",
        "pearson_ic",
        "ic_tstat",
        "hit_rate",
        "p_value",
        "newey_west_tstat",
        "bootstrap_ci_low",
        "bootstrap_ci_high",
        "turnover",
        "average_names_held",
        "concentration_hhi",
        "portfolio_beta",
        "sector_beta",
        "oil_beta",
        "gas_beta",
        "size_exposure",
        "value_exposure",
        "leverage_exposure",
        "momentum_exposure",
        "bid_ask_cost",
        "short_borrow_cost",
        "slippage",
        "average_filing_delay_days",
        "failed_extraction_rate",
    ],
}

PIT_AUDIT_COLUMNS = [
    "audit_id",
    "ticker",
    "signal_quarter",
    "rebalance_date",
    "filing_type",
    "accession_number",
    "filing_date",
    "accepted_datetime",
    "data_available_before_rebalance",
    "metric_name",
    "metric_value",
    "score_used",
    "rank_used",
    "portfolio_bucket",
    "execution_price_source",
    "execution_price",
    "return_start_date",
    "return_end_date",
    "holding_period_return",
    "notes",
]


def _read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def setup_module():
    populate_proof_ledgers()
    generate_universe_ledger()
    run_performance_ledger()
    generate_audit_example()
    run_eog_dcf()
    export_website_json()


def test_compute_composite():
    df = pd.DataFrame(
        {
            "ticker": ["EOG"],
            "quarter": ["2026-03-31"],
            "pct_oil_hedged_ntm": [0.52],
            "weighted_floor": [62.0],
            "tier1_years": [15.0],
            "fd_cost_per_boe": [10.0],
            "cash_opex_per_boe": [6.0],
        }
    )
    scores = compute_composite(df)
    assert not scores.empty
    assert "caligula_score" in scores.columns
    assert scores["caligula_score"].iloc[0] > 0


def test_reserve_bucket_tv():
    # Test bucket generation runs without error
    tv = calculate_reserve_bucket_tv("EOG", 0.0877)
    assert tv > 0


def test_extraction_ledger_schema():
    rows = _read_csv(AUDIT_DIR / "extraction_ledger.csv")
    assert rows
    assert list(rows[0].keys()) == REQUIRED_COLUMNS[AUDIT_DIR / "extraction_ledger.csv"]


def test_reserve_ledger_schema():
    path = DATA_DIR / "normalized" / "reserve_ledger.csv"
    rows = _read_csv(path)
    assert rows
    assert list(rows[0].keys()) == REQUIRED_COLUMNS[path]


def test_universe_ledger_schema():
    path = BACKTEST_DIR / "universe_ledger.csv"
    rows = _read_csv(path)
    assert rows
    assert list(rows[0].keys()) == REQUIRED_COLUMNS[path]


def test_performance_ledger_schema():
    path = BACKTEST_DIR / "performance_ledger.csv"
    rows = _read_csv(path)
    assert rows
    assert list(rows[0].keys()) == REQUIRED_COLUMNS[path]


def test_pit_audit_example_generation():
    path = BACKTEST_DIR / "pit_audit_examples.csv"
    rows = _read_csv(path)
    assert rows
    assert list(rows[0].keys()) == PIT_AUDIT_COLUMNS
    assert rows[0]["data_available_before_rebalance"] == "True"


def test_website_json_export():
    path = WEBSITE_DIR / "public_caligula_data.json"
    assert path.exists()
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    assert payload["generated_at"]
    assert payload["dcf_summary"]
    assert payload["performance_ledger"]


def test_dashboard_static_only_behavior():
    dashboard_path = ROOT / "caligula" / "dashboard" / "app.py"
    tree = ast.parse(dashboard_path.read_text(encoding="utf-8"))
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    forbidden_imports = {
        "caligula.backtest",
        "caligula.scoring",
        "caligula.valuation",
    }
    forbidden_calls = {
        "mean",
        "median",
        "std",
        "sum",
        "rank",
        "sort_values",
        "pct_change",
        "corr",
    }
    called_attrs = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }

    assert imported_modules.isdisjoint(forbidden_imports)
    assert called_attrs.isdisjoint(forbidden_calls)


def test_no_missing_required_ledger_fields():
    for path, columns in REQUIRED_COLUMNS.items():
        rows = _read_csv(path)
        assert rows, f"{path} has no rows"
        for row in rows:
            assert set(columns).issubset(row.keys())
            assert all(row[column] is not None for column in columns)
