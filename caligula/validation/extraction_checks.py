"""Extraction validation checks for the Caligula audit ledger."""

import csv
from caligula.config import AUDIT_DIR, VALIDATION_DIR

REQUIRED_FIELDS = [
    "extraction_id",
    "ticker",
    "fiscal_year",
    "filing_type",
    "accession_number",
    "filing_date",
    "source_section",
    "metric_name",
    "extracted_value",
    "raw_extracted_text",
    "model_name",
    "prompt_version",
    "confidence_score",
    "audit_hash",
]


def validate_extraction_ledger():
    filepath = AUDIT_DIR / "extraction_ledger.csv"
    if not filepath.exists():
        return

    total_records = 0
    passed = 0
    failed = 0
    warnings = 0
    human_review = 0

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_records += 1
            row_failed = False

            for field in REQUIRED_FIELDS:
                if not row.get(field):
                    row_failed = True
                    break

            if row_failed:
                failed += 1
                continue

            try:
                conf = float(row["confidence_score"])
                val = float(row["extracted_value"])
            except ValueError:
                failed += 1
                continue

            if conf < 0.0 or conf > 1.0:
                failed += 1
                continue

            if "reserve" in row["metric_name"].lower() and val < 0:
                failed += 1
                continue

            if "production" in row["metric_name"].lower() and val < 0:
                failed += 1
                continue

            if conf < 0.85:
                warnings += 1
                human_review += 1

            passed += 1

    summary_path = VALIDATION_DIR / "extraction_validation_summary.csv"
    file_exists = summary_path.exists()

    import datetime

    fail_rate = failed / total_records if total_records > 0 else 0
    review_rate = human_review / total_records if total_records > 0 else 0

    with open(summary_path, "a", newline="", encoding="utf-8") as f:
        fieldnames = [
            "run_id",
            "run_timestamp",
            "total_records",
            "passed_records",
            "failed_records",
            "warning_records",
            "failed_extraction_rate",
            "low_confidence_rate",
            "human_review_rate",
            "override_rate",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        writer.writerow(
            {
                "run_id": f"val_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                "run_timestamp": datetime.datetime.now(
                    datetime.timezone.utc
                ).isoformat(),
                "total_records": total_records,
                "passed_records": passed,
                "failed_records": failed,
                "warning_records": warnings,
                "failed_extraction_rate": fail_rate,
                "low_confidence_rate": review_rate,
                "human_review_rate": review_rate,
                "override_rate": 0.0,
            }
        )


if __name__ == "__main__":
    validate_extraction_ledger()
