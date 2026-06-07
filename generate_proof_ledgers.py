import datetime
from pathlib import Path
from caligula.ingestion.extraction_audit import log_extraction
from caligula.normalization.reserve_mapping import (
    write_reserve_ledger,
    reconcile_reserves,
)


def populate_proof_ledgers():
    for path in [
        Path("data/audit/extraction_ledger.csv"),
        Path("data/normalized/reserve_ledger.csv"),
    ]:
        if path.exists():
            path.unlink()

    # 1. Extraction Ledger
    log_extraction(
        {
            "ticker": "EOG",
            "fiscal_year": 2026,
            "filing_type": "10-Q",
            "filing_accession": "0000821189-26-000010",
            "filing_date": "2026-05-02",
            "accepted_datetime": "2026-05-02T16:05:00Z",
            "source_url": "https://sec.gov/...",
            "source_table": "Derivatives",
            "source_page": "14",
            "source_text_hash": "abc123hash",
            "raw_extracted_text": "we hedged 52% of NTM",
            "field_name": "pct_oil_hedged_ntm",
            "extracted_value": 0.52,
            "unit": "pct",
            "prompt_version": "v1",
            "model_name": "gemini-1.5-flash",
            "confidence_score": 0.95,
            "human_override_flag": False,
            "override_reason": "",
            "audit_hash": "validhash123",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    )

    # 2. Reserve Ledger
    record = {
        "ticker": "EOG",
        "fiscal_year": 2026,
        "proved_developed": 200.0,
        "proved_undeveloped": 150.0,
        "total_proved": 350.0,
        "oil_mmbbl": 175.0,
        "gas_bcf": 600.0,  # 100 boe
        "ngl_mmbbl": 75.0,
        "total_mmboe": 350.0,
        "standardized_measure": 15000.0,
        "prior_reserves": 300.0,
        "extensions_discoveries": 100.0,
        "revisions": -10.0,
        "purchases": 0.0,
        "sales": 0.0,
        "production_mmboe": 40.0,
        "source_filing_accession": "0000821189-26-000010",
        "audit_hash": "reserves_hash_123",
    }
    reconcile_reserves(record)
    write_reserve_ledger(record)


if __name__ == "__main__":
    populate_proof_ledgers()
