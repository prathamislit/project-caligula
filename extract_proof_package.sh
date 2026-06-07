#!/usr/bin/env bash
set -e

mkdir -p proof_package/logs
mkdir -p proof_package/files
mkdir -p proof_package/samples

echo "=== 1. SYSTEM INFO ===" | tee proof_package/logs/00_system_info.log
pwd | tee -a proof_package/logs/00_system_info.log
python --version | tee -a proof_package/logs/00_system_info.log
git status --short | tee -a proof_package/logs/00_system_info.log || true
git rev-parse --short HEAD | tee -a proof_package/logs/00_system_info.log || true

echo "=== 2. FILE TREE ==="
tree -L 4 | tee proof_package/logs/01_tree_L4.log || find . -maxdepth 4 -print | sort | tee proof_package/logs/01_tree_L4.log

echo "=== 3. FULL FILE INVENTORY ==="
find . -type f \
  -not -path "./.git/*" \
  -not -path "./.venv/*" \
  -not -path "./venv/*" \
  -not -path "*/__pycache__/*" \
  | sort | tee proof_package/logs/02_file_inventory.log

echo "=== 4. RUN SCANS ==="
make run-scans 2>&1 | tee proof_package/logs/03_make_run_scans.log

echo "=== 5. RUN TESTS ==="
make test 2>&1 | tee proof_package/logs/04_make_test.log

echo "=== 6. RUN FULL PIPELINE ==="
make all 2>&1 | tee proof_package/logs/05_make_all.log

echo "=== 7. DIRECT MODULE CHECKS ==="
{
  python -m caligula.validation.inventory_scan
  python -m caligula.validation.no_stub_scan
  python -m caligula.backtest.audit_example
  python -m caligula.exports.website_public
} 2>&1 | tee proof_package/logs/06_direct_module_checks.log

echo "=== 8. STUB / FAKE OUTPUT SCAN ==="
grep -RIn \
  "TODO\|FIXME\|pass$\|NotImplementedError\|placeholder\|dummy\|mock\|stub\|fake\|hardcoded\|sample data\|coming soon" \
  --exclude="no_stub_scan.py" \
  --exclude="stub_allowlist.yml" \
  caligula tests Makefile .flake8 \
  2>&1 | tee proof_package/logs/07_stub_fake_scan.log || true

echo "=== 9. FALLBACK / SILENT FAILURE SCAN ==="
grep -RIn \
  "except Exception\|return None\|return {}\|return \[\]\|fallback\|default.*metric" \
  caligula \
  2>&1 | tee proof_package/logs/08_fallback_scan.log || true

echo "=== 10. DASHBOARD COMPUTATION SCAN ==="
grep -RIn \
  "sharpe\|rank\|score\|valuation\|wacc\|terminal\|fallback\|default_metric" \
  caligula/dashboard \
  2>&1 | tee proof_package/logs/09_dashboard_scan.log || true

echo "=== 11. VALUATION / CLAIM LANGUAGE SCAN ==="
CLAIM_SCAN_TARGETS=(
  caligula
  tests
  README.md
  README_VERCEL.md
  EOG_DCF_Writeup.md
  build_excel_dcf.py
  compile_writeup_pdf.py
  Makefile
  config
  outputs/website
)

grep -RIn \
  "Valuation Date\|Recommend Long\|Strong Buy\|alpha-generating\|market-beating\|production-ready\|institutional-grade" \
  "${CLAIM_SCAN_TARGETS[@]}" \
  --exclude-dir=.git \
  --exclude-dir=.venv \
  --exclude-dir=venv \
  --exclude-dir=proof_package \
  --exclude-dir=.pytest_cache \
  --exclude-dir=outputs/logs \
  --exclude=proof_logs.txt \
  --exclude=caligula_proof_package.zip \
  --exclude=extract_proof_package.sh \
  2>&1 | tee proof_package/logs/10_claim_language_scan.log || true

echo "=== 12. COPY REQUIRED FILES ==="

copy_if_exists () {
  src="$1"
  if [ -f "$src" ]; then
    cp "$src" "proof_package/files/$(basename "$src")"
    echo "FOUND: $src"
  else
    echo "MISSING: $src"
  fi
}

copy_if_exists "data/audit/extraction_ledger.csv"
copy_if_exists "data/normalized/reserve_ledger.csv"
copy_if_exists "data/backtest/universe_ledger.csv"
copy_if_exists "data/backtest/performance_ledger.csv"
copy_if_exists "data/backtest/pit_audit_examples.csv"
copy_if_exists "outputs/website/public_caligula_data.json"
copy_if_exists "caligula/dashboard/app.py"
copy_if_exists "EOG_DCF_Writeup.md"
copy_if_exists "Makefile"
copy_if_exists ".flake8"

echo "=== 13. LEDGER SAMPLES ==="

for f in \
  data/audit/extraction_ledger.csv \
  data/normalized/reserve_ledger.csv \
  data/backtest/universe_ledger.csv \
  data/backtest/performance_ledger.csv \
  data/backtest/pit_audit_examples.csv
do
  echo ""
  echo "===== $f =====" | tee -a proof_package/logs/11_ledger_samples.log
  if [ -f "$f" ]; then
    echo "--- HEADER ---" | tee -a proof_package/logs/11_ledger_samples.log
    head -1 "$f" | tee -a proof_package/logs/11_ledger_samples.log
    echo "--- FIRST 10 ROWS ---" | tee -a proof_package/logs/11_ledger_samples.log
    head -11 "$f" | tee -a proof_package/logs/11_ledger_samples.log
  else
    echo "MISSING" | tee -a proof_package/logs/11_ledger_samples.log
  fi
done

echo "=== 14. JSON SAMPLE ===" | tee proof_package/logs/12_json_sample.log
if [ -f "outputs/website/public_caligula_data.json" ]; then
  python -m json.tool outputs/website/public_caligula_data.json | head -120 | tee -a proof_package/logs/12_json_sample.log
else
  echo "MISSING outputs/website/public_caligula_data.json" | tee -a proof_package/logs/12_json_sample.log
fi

echo "=== 15. SCHEMA VALIDATION CHECK ===" | tee proof_package/logs/13_schema_check.log

python <<'PY' 2>&1 | tee -a proof_package/logs/13_schema_check.log
import csv
from pathlib import Path

required = {
    "data/audit/extraction_ledger.csv": [
        "ticker","fiscal_year","filing_type","filing_accession","filing_date",
        "accepted_datetime","source_url","source_table","source_page",
        "source_text_hash","raw_extracted_text","field_name","extracted_value",
        "unit","prompt_version","model_name","confidence_score",
        "human_override_flag","override_reason","audit_hash","created_at"
    ],
    "data/normalized/reserve_ledger.csv": [
        "ticker","fiscal_year","proved_developed","proved_undeveloped",
        "total_proved","oil_mmbbl","gas_bcf","ngl_mmbbl","total_mmboe",
        "standardized_measure","production_mmboe","extensions_discoveries",
        "revisions","purchases","sales","source_filing_accession","audit_hash"
    ],
    "data/backtest/universe_ledger.csv": [
        "rebalance_date","ticker","eligible_flag","inclusion_reason",
        "exclusion_reason","listing_status","market_cap","adv_30d",
        "filing_available_flag","latest_filing_used","latest_filing_date",
        "latest_filing_accepted_datetime","sector","basin",
        "delisting_return_applied"
    ],
    "data/backtest/performance_ledger.csv": [
        "long_return","short_return","long_short_return","benchmark_return",
        "excess_return","cagr","annualized_volatility","sharpe","sortino",
        "max_drawdown","calmar","spearman_ic","pearson_ic","ic_tstat",
        "hit_rate","p_value","newey_west_tstat","bootstrap_ci_low",
        "bootstrap_ci_high","turnover","average_names_held",
        "concentration_hhi","portfolio_beta","sector_beta","oil_beta",
        "gas_beta","size_exposure","value_exposure","leverage_exposure",
        "momentum_exposure","bid_ask_cost","short_borrow_cost","slippage",
        "average_filing_delay_days","failed_extraction_rate"
    ],
}

ok = True

for file, cols in required.items():
    path = Path(file)
    print(f"\nChecking {file}")
    if not path.exists():
        print("MISSING FILE")
        ok = False
        continue

    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration:
            print("EMPTY FILE")
            ok = False
            continue

    missing = [c for c in cols if c not in header]
    extra = [c for c in header if c not in cols]

    if missing:
        print("MISSING COLUMNS:", missing)
        ok = False
    else:
        print("REQUIRED COLUMNS PRESENT")

    if extra:
        print("EXTRA COLUMNS:", extra)

if not ok:
    raise SystemExit(1)

print("\nSCHEMA CHECK PASSED")
PY

echo "=== 16. PACKAGE RESULTS ==="
zip -r caligula_proof_package.zip proof_package >/dev/null
echo "Created: caligula_proof_package.zip"

echo "=== DONE ==="
