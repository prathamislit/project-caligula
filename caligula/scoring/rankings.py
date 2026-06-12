"""Execute scoring pipeline and generate canonical ranking outputs.

Consumes the real backtest score panel (data/scores/all_scores.parquet,
produced by run_backtest.py / src.backtest.score_history) and writes the
canonical quarterly tables. No sample or placeholder data.
"""

import csv

import pandas as pd
from caligula.config import DATA_DIR, TABLES_DIR
from caligula.errors import CaligulaDataError

SCORES_PANEL = DATA_DIR / "scores" / "all_scores.parquet"

_PILLAR_COLS = [
    "unit_economics_score",
    "capital_discipline_score",
    "balance_sheet_score",
    "hedge_book_score",
    "reserves_score",
    "operational_score",
    "sentiment_score",
    "macro_sensitivity_score",
]


def _write_methodology_table():
    methodology_path = TABLES_DIR / "pillar_methodology.csv"
    methodology_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "pillar_id",
        "pillar_name",
        "metric_name",
        "raw_formula",
        "direction",
        "normalization",
        "winsorization",
        "missing_data_rule",
        "weight",
        "source_type",
        "source_table",
        "rebalance_lag",
        "notes",
    ]

    with open(methodology_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(
            {
                "pillar_id": "P1",
                "pillar_name": "Hedge Book",
                "metric_name": "NTM Hedge Floor Coverage",
                "raw_formula": "hedged_ntm_volume * weighted_floor",
                "direction": "higher_is_better",
                "normalization": "min_max_0_1",
                "winsorization": "none",
                "missing_data_rule": "neutral_0.5",
                "weight": "0.125",
                "source_type": "SEC filing hedge footnote",
                "source_table": "Derivative instruments table",
                "rebalance_lag": "filing_cutoff_plus_next_rebalance",
                "notes": "",
            }
        )
        # Other pillars can be added similarly.


def load_score_panel() -> pd.DataFrame:
    """Load the real quarterly score panel produced by the backtest pipeline."""
    if not SCORES_PANEL.exists():
        raise CaligulaDataError(
            f"Score panel not found at {SCORES_PANEL}. "
            "Run `python run_backtest.py` first to generate real scores."
        )
    df = pd.read_parquet(SCORES_PANEL)
    if df.empty or "caligula_score" not in df.columns:
        raise CaligulaDataError(f"Score panel at {SCORES_PANEL} is empty or malformed.")
    return df


def run_scoring_pipeline():
    """Write canonical ranking tables from the real score panel."""
    _write_methodology_table()

    panel = load_score_panel()
    panel = panel.copy()
    panel["quarter"] = pd.to_datetime(panel["quarter"])

    # Rank within each quarter (1 = highest composite score)
    panel["rank"] = (
        panel.groupby("quarter")["caligula_score"]
        .rank(ascending=False, method="min")
    )
    panel = panel.sort_values(["quarter", "rank"])

    pillar_cols = [c for c in _PILLAR_COLS if c in panel.columns]
    base_cols = ["ticker", "quarter"] + pillar_cols + ["caligula_score", "rank", "tier"]

    panel[base_cols].to_csv(TABLES_DIR / "pillar_scores_quarterly.csv", index=False)
    panel[["ticker", "quarter", "caligula_score", "rank", "tier"]].to_csv(
        TABLES_DIR / "composite_scores_quarterly.csv", index=False
    )
    panel[["ticker", "quarter", "rank", "tier"]].to_csv(
        TABLES_DIR / "rankings_quarterly.csv", index=False
    )


if __name__ == "__main__":
    run_scoring_pipeline()
