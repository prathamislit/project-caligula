"""Map extracted reserve metrics and run roll-forward reconciliations."""

import csv
from caligula.config import DATA_DIR


def write_reserve_ledger(record: dict):
    # Enforce data/normalized/reserve_ledger.csv
    normalized_dir = DATA_DIR / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)
    filepath = normalized_dir / "reserve_ledger.csv"

    file_exists = filepath.exists()
    fieldnames = [
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
    ]
    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        row = {k: record.get(k, "") for k in fieldnames}
        writer.writerow(row)


def reconcile_reserves(record: dict):
    """
    Tolerance must be explicit.
    - proved_developed + proved_undeveloped ≈ total_proved (tolerance: 0.1)
    - oil + gas/6 + ngl ≈ total_mmboe (tolerance: 0.1)
    - prior + extensions + revisions + purchases - sales - production ≈ ending
      reserves (tolerance: 0.1)
    """
    errors = []

    pd = float(record.get("proved_developed", 0))
    pud = float(record.get("proved_undeveloped", 0))
    tp = float(record.get("total_proved", 0))

    if abs((pd + pud) - tp) > 0.1:
        errors.append("PD + PUD != Total Proved")

    oil = float(record.get("oil_mmbbl", 0))
    gas = float(record.get("gas_bcf", 0))
    ngl = float(record.get("ngl_mmbbl", 0))
    boe = float(record.get("total_mmboe", 0))

    if abs((oil + (gas / 6.0) + ngl) - boe) > 0.1:
        errors.append("Commodity components != Total BOE")

    # Simplified rollforward check assuming prior is passed in
    prior = float(record.get("prior_reserves", 0))
    ext = float(record.get("extensions_discoveries", 0))
    rev = float(record.get("revisions", 0))
    pur = float(record.get("purchases", 0))
    sales = float(record.get("sales", 0))
    prod = float(record.get("production_mmboe", 0))

    calc_ending = prior + ext + rev + pur - sales - prod
    if abs(calc_ending - tp) > 0.1 and prior > 0:
        errors.append("Roll-forward does not reconcile")

    if errors:
        raise ValueError(
            "Reserve reconciliation failed for "
            f"{record.get('ticker')}: {', '.join(errors)}"
        )
