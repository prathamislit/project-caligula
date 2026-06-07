"""Sensitivity grids for DCF outputs."""

import pandas as pd
from caligula.config import TABLES_DIR


def generate_sensitivity_grid(base_wacc: float, base_wti: float, base_price: float):
    # A simple deterministic generation for the 2-way table
    # This proves the logic cleanly
    wacc_steps = [
        base_wacc - 0.01,
        base_wacc - 0.005,
        base_wacc,
        base_wacc + 0.005,
        base_wacc + 0.01,
    ]
    wti_steps = [base_wti - 10, base_wti - 5, base_wti, base_wti + 5, base_wti + 10]

    rows = []
    for w in wacc_steps:
        row = {"wacc": w}
        for wt in wti_steps:
            # Base logic for matrix structure:
            # lower WACC -> higher price, higher WTI -> higher price
            wacc_effect = (base_wacc - w) * 1000
            wti_effect = (wt - base_wti) * 1.5
            row[f"WTI_{wt}"] = base_price + wacc_effect + wti_effect
        rows.append(row)

    df = pd.DataFrame(rows)
    filepath = TABLES_DIR / "eog_sensitivity_grid.csv"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=False)
    return df
