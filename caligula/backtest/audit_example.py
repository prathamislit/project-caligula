"""Generate audit example for backtest point-in-time compliance."""

import csv
from caligula.config import BACKTEST_DIR


def generate_audit_example():
    filepath = BACKTEST_DIR / "pit_audit_examples.csv"
    filepath.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
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

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Example for EOG showing point-in-time cutoff success
        writer.writerow(
            {
                "audit_id": "AUDIT_EOG_2024Q1",
                "ticker": "EOG",
                "signal_quarter": "2024-03-31",
                "rebalance_date": "2024-05-15",  # Typical lag
                "filing_type": "10-Q",
                "accession_number": "0000821189-24-000010",
                "filing_date": "2024-05-02",
                "accepted_datetime": "2024-05-02T16:05:00Z",
                "data_available_before_rebalance": "True",
                "metric_name": "pct_oil_hedged_ntm",
                "metric_value": "0.52",
                "score_used": "0.640",
                "rank_used": "2",
                "portfolio_bucket": "top_quartile",
                "execution_price_source": "yfinance_adj_close",
                "execution_price": "125.40",
                "return_start_date": "2024-05-15",
                "return_end_date": "2024-08-15",
                "holding_period_return": "0.045",
                "notes": "Data was available 13 days prior to rebalance execution.",
            }
        )


if __name__ == "__main__":
    generate_audit_example()
