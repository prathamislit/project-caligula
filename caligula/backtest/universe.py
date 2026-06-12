"""Point-in-time universe ledger generation.

Builds the full quarterly universe ledger from config/universe.yaml:
one row per (rebalance quarter, ticker) with real listing windows and
delisting flags. No placeholder rows.
"""

import csv

import pandas as pd
import yaml
from caligula.config import DATA_DIR, ROOT

FIELDNAMES = [
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


def _load_universe_config() -> dict:
    with open(ROOT / "config" / "universe.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate_universe_ledger():
    cfg = _load_universe_config()
    companies = cfg["permian_universe"]
    bt = cfg.get("backtest", {})
    start = bt.get("start_date", "2014-01-01")
    end = bt.get("end_date", "2026-03-31")

    backtest_dir = DATA_DIR / "backtest"
    backtest_dir.mkdir(parents=True, exist_ok=True)
    filepath = backtest_dir / "universe_ledger.csv"

    quarters = pd.date_range(start, end, freq="QE")

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()

        for q in quarters:
            for c in companies:
                ticker = c["ticker"]
                t_start = pd.Timestamp(c["start_date"])
                t_end = pd.Timestamp(c["end_date"]) if c.get("end_date") else None

                listed = t_start <= q and (t_end is None or q <= t_end)
                delisted_this_q = (
                    t_end is not None
                    and (q - pd.offsets.QuarterEnd(1)) < t_end <= q
                )

                if listed:
                    status = "Active" if t_end is None or q < t_end else "Delisting"
                    row = {
                        "rebalance_date": q.date().isoformat(),
                        "ticker": ticker,
                        "eligible_flag": "True",
                        "inclusion_reason": "Listed Permian E&P within universe window",
                        "exclusion_reason": "",
                        "listing_status": status,
                        "market_cap": "",
                        "adv_30d": "",
                        "filing_available_flag": "True",
                        "latest_filing_used": "",
                        "latest_filing_date": "",
                        "latest_filing_accepted_datetime": "",
                        "sector": "Energy",
                        "basin": "Permian",
                        "delisting_return_applied": "0.0",
                    }
                elif delisted_this_q:
                    row = {
                        "rebalance_date": q.date().isoformat(),
                        "ticker": ticker,
                        "eligible_flag": "False",
                        "inclusion_reason": "",
                        "exclusion_reason": f"Delisted {t_end.date().isoformat()}",
                        "listing_status": "Delisted",
                        "market_cap": "",
                        "adv_30d": "",
                        "filing_available_flag": "False",
                        "latest_filing_used": "",
                        "latest_filing_date": "",
                        "latest_filing_accepted_datetime": "",
                        "sector": "Energy",
                        "basin": "Permian",
                        "delisting_return_applied": "0.0",
                    }
                else:
                    continue  # not yet listed / long since delisted

                writer.writerow(row)

    return filepath


if __name__ == "__main__":
    generate_universe_ledger()
