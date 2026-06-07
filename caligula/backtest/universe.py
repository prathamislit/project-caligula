"""Point-in-time universe ledger generation."""

import csv
from caligula.config import DATA_DIR


def generate_universe_ledger():
    backtest_dir = DATA_DIR / "backtest"
    backtest_dir.mkdir(parents=True, exist_ok=True)
    filepath = backtest_dir / "universe_ledger.csv"

    fieldnames = [
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
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Output example record
        writer.writerow(
            {
                "rebalance_date": "2026-05-15",
                "ticker": "EOG",
                "eligible_flag": "True",
                "inclusion_reason": "Passes liquidity and sector screen",
                "exclusion_reason": "",
                "listing_status": "Active",
                "market_cap": "81000000000",
                "adv_30d": "500000000",
                "filing_available_flag": "True",
                "latest_filing_used": "10-Q",
                "latest_filing_date": "2026-05-02",
                "latest_filing_accepted_datetime": "2026-05-02T16:05:00Z",
                "sector": "Energy",
                "basin": "Permian",
                "delisting_return_applied": "0.0",
            }
        )


if __name__ == "__main__":
    generate_universe_ledger()
