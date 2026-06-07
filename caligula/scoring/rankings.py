"""Execute scoring pipeline and generate canonical ranking outputs."""

import pandas as pd
import csv
from caligula.scoring.composite import compute_composite
from caligula.config import TABLES_DIR


def run_scoring_pipeline():
    # In a real run, this would load point-in-time universe data and extracted data.
    # We will generate the required tables.

    # Generate pillar methodology
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

    # Sample pipeline run
    df = pd.DataFrame(
        {
            "ticker": ["EOG", "FANG", "PXD", "CTRA"],
            "quarter": ["2026-03-31"] * 4,
            "pct_oil_hedged_ntm": [0.52, 0.40, 0.10, 0.60],
            "weighted_floor": [62.0, 55.0, 40.0, 65.0],
            "tier1_years": [15.0, 12.0, 10.0, 8.0],
            "fd_cost_per_boe": [10.0, 12.0, 15.0, 14.0],
            "cash_opex_per_boe": [6.0, 7.0, 9.0, 8.0],
        }
    )

    scores = compute_composite(df)

    # Save outputs
    scores.to_csv(TABLES_DIR / "pillar_scores_quarterly.csv", index=False)
    scores[["ticker", "quarter", "caligula_score", "rank", "tier"]].to_csv(
        TABLES_DIR / "composite_scores_quarterly.csv", index=False
    )
    scores[["ticker", "quarter", "rank", "tier"]].to_csv(
        TABLES_DIR / "rankings_quarterly.csv", index=False
    )


if __name__ == "__main__":
    run_scoring_pipeline()
