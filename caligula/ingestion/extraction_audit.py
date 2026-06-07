"""Audit trail and hashing for AI extraction."""

import hashlib
import json
import csv
import datetime
from typing import Any, Dict
from ..config import AUDIT_DIR


def canonical_json(payload: Dict[str, Any]) -> str:
    """Return deterministic JSON string for hashing."""
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )


def compute_audit_hash(payload: Dict[str, Any]) -> str:
    """Return SHA-256 hash for extraction audit payload."""
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def log_extraction(record: Dict[str, Any]):
    """Appends an extraction record to the extraction_ledger.csv"""
    filepath = AUDIT_DIR / "extraction_ledger.csv"
    file_exists = filepath.exists()

    fieldnames = [
        "ticker",
        "fiscal_year",
        "filing_type",
        "filing_accession",
        "filing_date",
        "accepted_datetime",
        "source_url",
        "source_table",
        "source_page",
        "source_text_hash",
        "raw_extracted_text",
        "field_name",
        "extracted_value",
        "unit",
        "prompt_version",
        "model_name",
        "confidence_score",
        "human_override_flag",
        "override_reason",
        "audit_hash",
        "created_at",
    ]

    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        # Ensure all fields are present, fill with empty string if missing
        row = {k: record.get(k, "") for k in fieldnames}

        # Set timestamps if not provided
        if not row.get("created_at"):
            row["created_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

        writer.writerow(row)


def log_extraction_failure(failure: Dict[str, Any]):
    """Appends an extraction failure to extraction_failures.csv"""
    filepath = AUDIT_DIR / "extraction_failures.csv"
    file_exists = filepath.exists()

    fieldnames = [
        "failure_id",
        "ticker",
        "fiscal_year",
        "fiscal_period",
        "filing_type",
        "accession_number",
        "filing_date",
        "metric_name",
        "source_section",
        "error_type",
        "error_message",
        "retry_count",
        "resolved",
        "resolution_method",
        "human_review_required",
        "created_at",
        "updated_at",
    ]

    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        row = {k: failure.get(k, "") for k in fieldnames}
        if not row.get("created_at"):
            row["created_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        writer.writerow(row)


def log_restatement(restatement: Dict[str, Any]):
    """Appends a restatement record to restatement_log.csv"""
    filepath = AUDIT_DIR / "restatement_log.csv"
    file_exists = filepath.exists()

    fieldnames = [
        "restatement_id",
        "ticker",
        "original_accession_number",
        "amended_accession_number",
        "original_filing_date",
        "amended_filing_date",
        "affected_fiscal_year",
        "affected_metric",
        "original_value",
        "amended_value",
        "delta",
        "delta_pct",
        "model_uses_amended_value",
        "reason",
        "created_at",
    ]

    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        row = {k: restatement.get(k, "") for k in fieldnames}
        if not row.get("created_at"):
            row["created_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        writer.writerow(row)
