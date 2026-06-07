"""Generate static public JSON for website."""

import json
import pandas as pd
from caligula.config import BACKTEST_DIR, TABLES_DIR, WEBSITE_DIR, VALUATION_DATE


def export_website_json():
    """Generates public.json used by the Next.js frontend."""
    # Attempt to load canonical outputs
    dcf_path = TABLES_DIR / "eog_dcf_outputs.csv"
    if dcf_path.exists():
        dcf_data = pd.read_csv(dcf_path).to_dict(orient="records")
    else:
        dcf_data = []

    ledger_path = BACKTEST_DIR / "performance_ledger.csv"
    if ledger_path.exists():
        ledger_data = pd.read_csv(ledger_path).to_dict(orient="records")
    else:
        ledger_data = []

    # Final structure for frontend
    payload = {
        "generated_at": VALUATION_DATE,
        "dcf_summary": dcf_data,
        "performance_ledger": ledger_data,
    }

    out_path = WEBSITE_DIR / "public_caligula_data.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


if __name__ == "__main__":
    export_website_json()
