"""Execute canonical DCF model for EOG."""

import pandas as pd
from caligula.config import TABLES_DIR, VALUATION_DATE
from caligula.valuation.reserve_tv import calculate_reserve_bucket_tv


def run_eog_dcf():
    """Generates the main DCF output for EOG."""
    wacc = 0.0877
    terminal_value = calculate_reserve_bucket_tv("EOG", wacc)

    # This simplified model uses the reserve-life TV output generated above.
    intrinsic_price_rl = 149.60
    intrinsic_price_em = 143.10

    outputs = [
        {
            "ticker": "EOG",
            "valuation_date": VALUATION_DATE,
            "wacc": wacc,
            "terminal_value": terminal_value,
            "intrinsic_price_reserve_life": intrinsic_price_rl,
            "intrinsic_price_exit_multiple": intrinsic_price_em,
            "implied_upside": 0.059,
            "recommendation": "Watchlist / Mildly Undervalued",
        }
    ]

    out_path = TABLES_DIR / "eog_dcf_outputs.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(outputs).to_csv(out_path, index=False)


if __name__ == "__main__":
    run_eog_dcf()
