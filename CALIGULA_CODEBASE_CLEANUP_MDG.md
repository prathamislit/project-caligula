# CALIGULA CODEBASE CLEANUP IMPLEMENTATION SPEC

## Objective

Clean the Caligula codebase before credibility upgrades.

Remove every stub, placeholder, duplicate, unused branch, fake implementation, dead file, and misleading artifact that weakens efficiency, readability, or trust.

This is a destructive cleanup pass.

Do not add new methodology features here.
Do not refactor for aesthetics alone.
Do not create more abstraction unless it removes duplication.
Do not leave TODO-driven code in production paths.

Target outcome:

- clean execution graph
- no dead stubs
- no fake metrics
- no unused model paths
- no placeholder data
- no tangled pipelines
- no duplicate methodology files
- no misleading UI labels
- no hidden broken functions
- no orphaned scripts
- no uncalled validation logic

---

# Priority Order

Execute in this order.

1. Remove fake or stubbed model paths.
2. Remove placeholder data and hardcoded fake outputs.
3. Collapse duplicate pipeline branches.
4. Delete unused scripts and orphaned files.
5. Simplify imports and dependencies.
6. Enforce one canonical data contract.
7. Enforce one canonical score path.
8. Enforce one canonical backtest path.
9. Enforce one canonical DCF output path.
10. Add cleanup validation gates.

No later step can preserve junk from an earlier step.

---

# Global Rule

Any file, function, class, API route, component, notebook, script, config, or data artifact must satisfy at least one condition:

1. It is used by the live website.
2. It is used by the Caligula research pipeline.
3. It is used by the DCF model.
4. It is used by validation or testing.
5. It is required documentation.

If none apply, delete it.

Do not keep files because they “might be useful later.”

---

# Forbidden Production Patterns

Remove or quarantine all production code containing:

- TODO
- FIXME
- placeholder
- dummy
- mock
- fake
- sample
- temp
- hardcoded
- coming soon
- pass-only functions
- empty except blocks
- silent fallbacks
- print debugging
- unused return values
- magic numbers without named constants
- metrics without source data
- manually typed performance results
- demo-only data inside production folders
- duplicated formulas across files
- unused feature flags
- dead CLI commands
- incomplete API endpoints
- UI cards not backed by real data

Allowed only inside:

- docs/archive/
- tests/fixtures/
- examples/

Even there, label clearly.

---

# Required Folder Structure

Normalize the project into this structure.

```text
project-caligula/
  README.md
  CLAUDE.md
  pyproject.toml
  requirements.lock
  .env.example
  .gitignore

  caligula/
    __init__.py
    config.py
    contracts.py
    paths.py

    ingestion/
      sec_fetch.py
      filing_index.py
      extraction.py
      extraction_audit.py

    normalization/
      units.py
      reserve_mapping.py
      factor_transforms.py

    scoring/
      pillars.py
      composite.py
      rankings.py

    backtest/
      portfolio.py
      returns.py
      metrics.py
      audit_example.py
      performance_ledger.py

    valuation/
      eog_dcf.py
      reserve_tv.py
      wacc.py
      sensitivities.py

    validation/
      data_quality.py
      point_in_time.py
      parity.py
      no_stub_scan.py

  data/
    raw/
    interim/
    processed/
    audit/
    ledgers/

  outputs/
    tables/
    charts/
    memos/
    website/

  tests/
    test_contracts.py
    test_extraction_audit.py
    test_point_in_time.py
    test_scoring.py
    test_backtest_metrics.py
    test_reserve_tv.py
    test_no_stubs.py

  docs/
    methodology/
    archive/
```

Anything outside this structure requires justification.

If unjustified, delete it.

---

# Cleanup Pass 1: Inventory Everything

Create one inventory file:

```text
outputs/tables/codebase_inventory.csv
```

Columns:

```text
path
file_type
line_count
imports
exports
referenced_by
references
purpose
status
cleanup_action
```

Allowed status values:

```text
KEEP
DELETE
MERGE
ARCHIVE
REWRITE
```

Allowed cleanup_action values:

```text
none
delete_unused
merge_duplicate
move_archive
replace_stub
remove_placeholder
simplify_imports
rewrite_contract
```

Command:

```bash
python -m caligula.validation.inventory_scan \
  --root . \
  --output outputs/tables/codebase_inventory.csv
```

Acceptance gate:

- every file has a status
- every DELETE file is removed
- every MERGE file is merged
- every ARCHIVE file is moved
- no unknown-purpose files remain

---

# Cleanup Pass 2: Stub Scan

Create:

```text
caligula/validation/no_stub_scan.py
```

It must fail if production code contains forbidden tokens.

Scan folders:

```text
caligula/
app/
src/
components/
pages/
lib/
scripts/
```

Ignore folders:

```text
docs/archive/
tests/fixtures/
examples/
node_modules/
.venv/
.next/
dist/
build/
```

Forbidden regex list:

```python
FORBIDDEN_PATTERNS = [
    r"\bTODO\b",
    r"\bFIXME\b",
    r"placeholder",
    r"dummy",
    r"mock",
    r"fake",
    r"sample data",
    r"coming soon",
    r"not implemented",
    r"pass\s*$",
    r"raise NotImplementedError",
    r"except Exception:\s*pass",
    r"console\.log",
    r"print\(",
]
```

Allowlist file:

```text
caligula/validation/stub_allowlist.yml
```

Allowlist must require:

```yaml
path:
  reason:
  expiry_date:
  owner:
```

No permanent allowlists.

Command:

```bash
python -m caligula.validation.no_stub_scan
```

Acceptance gate:

- zero forbidden production stubs
- no expired allowlist entries
- no broad allowlist patterns

---

# Cleanup Pass 3: Delete Fake Outputs

Search and remove all manually entered research outputs.

Especially delete or regenerate:

- hardcoded Sharpe
- hardcoded CAGR
- hardcoded IC
- hardcoded hit rate
- hardcoded upside
- hardcoded rank
- hardcoded valuation date
- hardcoded price
- hardcoded WACC output
- hardcoded sensitivity grid
- static chart images not generated by pipeline
- frontend metric cards using literal numbers

All visible metrics must come from files in:

```text
outputs/tables/
outputs/charts/
outputs/website/
```

Required canonical public export:

```text
outputs/website/caligula_public_metrics.json
```

Website must read from this file only.

No metric literals inside React components.

Acceptance gate:

```bash
rg "Sharpe|CAGR|IC|hit rate|upside|WACC|valuation date|rank" app src components pages lib
```

Every match must be either:

- a label
- a data key
- a formatter
- imported from canonical JSON

No literal model outputs.

---

# Cleanup Pass 4: One Canonical Data Contract

Create one contract file:

```text
caligula/contracts.py
```

Define canonical schemas using Pydantic or dataclasses.

Required contracts:

```python
FilingRecord
ExtractionRecord
ReserveRecord
HedgeRecord
PillarInputRecord
PillarScoreRecord
CompositeScoreRecord
UniverseMemberRecord
BacktestHoldingRecord
BacktestReturnRecord
PerformanceMetricRecord
DCFInputRecord
DCFOutputRecord
```

Delete competing schema definitions.

No dictionaries passed across major pipeline stages.

Allowed:

- dict for JSON serialization only
- typed record internally

Acceptance gate:

- no duplicated schema classes
- no unnamed tuple outputs
- no major function returning raw mixed dictionaries

---

# Cleanup Pass 5: One Canonical Extraction Path

There must be exactly one extraction pipeline.

Canonical path:

```text
SEC filing -> raw text/table -> Gemini extraction -> normalized record -> audit ledger -> reviewed record -> model input
```

Delete or archive alternative paths:

- old regex-only reserve extractor
- old manual CSV loader
- experimental Gemini parser
- notebook-only parser
- one-off EOG parser
- copied parser inside website folder

Keep only if used by tests or archive.

Required live files:

```text
caligula/ingestion/sec_fetch.py
caligula/ingestion/filing_index.py
caligula/ingestion/extraction.py
caligula/ingestion/extraction_audit.py
caligula/normalization/reserve_mapping.py
```

Acceptance gate:

- one public extraction entrypoint
- one audit ledger output
- one normalized reserve output
- no duplicate parser logic

---

# Cleanup Pass 6: One Canonical Scoring Path

There must be exactly one scoring flow.

Canonical path:

```text
normalized inputs -> pillar transforms -> pillar scores -> composite score -> rankings
```

Required files:

```text
caligula/scoring/pillars.py
caligula/scoring/composite.py
caligula/scoring/rankings.py
```

Delete or archive:

- old scoring notebooks
- duplicate ranking scripts
- static score CSVs
- manually adjusted scores
- frontend-side scoring
- ad hoc EOG rank calculators
- previous v1/v2 score branches

Required outputs:

```text
outputs/tables/pillar_methodology.csv
outputs/tables/pillar_scores_quarterly.csv
outputs/tables/composite_scores_quarterly.csv
outputs/tables/rankings_quarterly.csv
```

Acceptance gate:

- no score generated outside scoring module
- no ranking logic in website code
- no manual rank override
- no competing composite formula

---

# Cleanup Pass 7: One Canonical Backtest Path

There must be exactly one backtest engine.

Canonical path:

```text
rankings -> point-in-time universe -> holdings -> returns -> metrics -> performance ledger
```

Required files:

```text
caligula/backtest/portfolio.py
caligula/backtest/returns.py
caligula/backtest/metrics.py
caligula/backtest/audit_example.py
caligula/backtest/performance_ledger.py
```

Delete or archive:

- vectorized prototype notebooks
- old long-short simulation scripts
- toy backtest code
- charts from deleted backtests
- frontend-calculated returns
- CSVs not tied to current run ID

Required run ID:

Every backtest output must include:

```text
run_id
as_of_date
signal_lag_rule
rebalance_rule
transaction_cost_rule
borrow_cost_rule
universe_version
scoring_version
```

Required outputs:

```text
outputs/tables/backtest_holdings.csv
outputs/tables/backtest_returns.csv
outputs/tables/performance_ledger.csv
outputs/tables/backtest_audit_example.csv
```

Acceptance gate:

- one backtest command
- one holdings ledger
- one returns ledger
- one performance ledger
- all website metrics read from ledger

---

# Cleanup Pass 8: One Canonical DCF Path

There must be exactly one EOG DCF model output path.

Canonical path:

```text
DCF inputs -> three-statement forecast -> FCFF -> reserve bucket TV -> sensitivities -> memo exports
```

Required files:

```text
caligula/valuation/eog_dcf.py
caligula/valuation/reserve_tv.py
caligula/valuation/wacc.py
caligula/valuation/sensitivities.py
```

Delete or archive:

- stale EOG valuation scripts
- static implied upside files
- manually typed DCF tables
- old Excel export scripts not used
- old reserve-life terminal scripts
- website DCF numbers typed by hand

Required outputs:

```text
outputs/tables/eog_dcf_inputs.csv
outputs/tables/eog_dcf_outputs.csv
outputs/tables/eog_reserve_bucket_tv.csv
outputs/tables/eog_wacc_bridge.csv
outputs/tables/eog_sensitivity_grid.csv
outputs/website/eog_dcf_public_metrics.json
```

Acceptance gate:

- one valuation date source
- one market data timestamp source
- no future-dated final valuation
- no hardcoded price in website
- no duplicate terminal value formulas

---

# Cleanup Pass 9: Dependency Pruning

Remove unused dependencies.

For Python:

```bash
pip install pipreqs pip-check-reqs
pipreqs . --force
pip-extra-reqs .
pip-missing-reqs .
```

For Node:

```bash
npx depcheck
```

Delete unused dependencies from:

```text
requirements.txt
pyproject.toml
package.json
```

Create lockfile:

```text
requirements.lock
```

Acceptance gate:

- no unused Python dependencies
- no unused Node dependencies
- no duplicated data libraries
- no unused charting libraries
- no abandoned AI SDKs
- no notebook-only packages in production requirements

---

# Cleanup Pass 10: Import Cleanup

Remove unused imports.

Python:

```bash
ruff check . --select F401,F841,I --fix
ruff format .
```

TypeScript / JavaScript:

```bash
npx eslint . --fix
npx prettier . --write
```

Acceptance gate:

- zero unused imports
- zero unused variables
- deterministic formatting
- no wildcard imports
- no circular imports

---

# Cleanup Pass 11: Remove Silent Failures

Delete all silent exception handling.

Forbidden:

```python
try:
    ...
except Exception:
    pass
```

Forbidden:

```python
except Exception:
    return None
```

Forbidden:

```python
except:
    print("error")
```

Required pattern:

```python
except SpecificError as exc:
    raise CaligulaPipelineError("Clear failure context") from exc
```

Create:

```text
caligula/errors.py
```

Define:

```python
CaligulaError
CaligulaDataError
CaligulaExtractionError
CaligulaPointInTimeError
CaligulaScoringError
CaligulaBacktestError
CaligulaValuationError
```

Acceptance gate:

- no bare except
- no silent pass
- no swallowed extraction failures
- all failed filings logged
- failed extraction rate computable

---

# Cleanup Pass 12: Remove Intertwined Website Logic

The website must not calculate research results.

Website can only:

- load public JSON
- render tables
- render charts
- link artifacts
- format values

Website cannot:

- compute ranks
- compute DCF upside
- compute performance metrics
- compute scores
- compute terminal values
- compute hedge cushion
- compute WACC
- store final numbers manually

Required public JSON files:

```text
outputs/website/caligula_public_metrics.json
outputs/website/eog_dcf_public_metrics.json
outputs/website/performance_ledger_public.json
outputs/website/methodology_public.json
```

Acceptance gate:

- all public numbers trace to output JSON
- output JSON trace to pipeline tables
- pipeline tables trace to run ID
- no calculation hidden in frontend

---

# Cleanup Pass 13: Archive, Do Not Delete Research History

Move obsolete but informative files to:

```text
docs/archive/YYYY-MM-DD_cleanup/
```

Archive only:

- old memos
- old methodology notes
- old notebooks
- old screenshots
- old output charts
- obsolete CSVs needed for provenance

Delete outright:

- generated caches
- duplicate build artifacts
- temp files
- broken scripts
- empty files
- unused copied components
- unused package lock duplicates

Create archive manifest:

```text
docs/archive/YYYY-MM-DD_cleanup/ARCHIVE_MANIFEST.md
```

Each archived item needs:

```text
old_path
new_path
reason_archived
replacement_path
```

Acceptance gate:

- no orphaned archive
- no live code imports archive files
- archive excluded from production build

---

# Cleanup Pass 14: Remove Notebooks From Production Flow

Notebooks are allowed only for exploration.

They cannot be required for:

- extraction
- scoring
- backtesting
- DCF outputs
- website numbers

Move notebooks to:

```text
docs/archive/notebooks/
```

If notebook logic is needed, convert it into modules.

Acceptance gate:

```bash
find . -name "*.ipynb"
```

Allowed result only under:

```text
docs/archive/notebooks/
```

---

# Cleanup Pass 15: Remove Duplicate CSVs

There must not be multiple CSVs claiming the same truth.

Canonical outputs:

```text
outputs/tables/extraction_audit_ledger.csv
outputs/tables/reserve_item_ledger.csv
outputs/tables/point_in_time_universe_ledger.csv
outputs/tables/pillar_methodology.csv
outputs/tables/performance_ledger.csv
outputs/tables/backtest_audit_example.csv
outputs/tables/eog_reserve_bucket_tv.csv
outputs/tables/eog_dcf_outputs.csv
```

Delete or archive CSVs with names like:

```text
final.csv
final_v2.csv
new_final.csv
cleaned.csv
test.csv
temp.csv
manual.csv
updated.csv
backup.csv
copy.csv
```

Acceptance gate:

- no ambiguous CSV names
- every CSV has a README entry
- every CSV has a producing command
- every CSV has a schema

---

# Cleanup Pass 16: Config Hygiene

All configuration belongs in:

```text
caligula/config.py
.env.example
```

Config must include:

```text
valuation_date
market_data_as_of
signal_lag_days
rebalance_frequency
transaction_cost_bps
short_borrow_bps
benchmark_ticker
oil_price_source
gas_price_source
risk_free_rate_source
gemini_model_name
gemini_prompt_version
```

No config literals inside pipeline functions.

Acceptance gate:

- no scattered constants
- no hidden API keys
- no hardcoded local absolute paths
- no personal machine paths
- no future valuation date unless explicitly marked draft

---

# Cleanup Pass 17: Naming Standards

Use direct, boring names.

Forbidden names:

```text
main2.py
new_model.py
better_model.py
test_run.py
final_model.py
final_final.py
misc.py
utils2.py
script.py
scratch.py
experiment.py
```

Allowed names describe function:

```text
extraction_audit.py
reserve_mapping.py
performance_ledger.py
point_in_time.py
reserve_tv.py
```

Acceptance gate:

- no vague filenames
- no numbered versions
- no unowned utility dumping grounds

---

# Cleanup Pass 18: Utility Function Control

Do not allow massive `utils.py` files.

Split utilities by domain:

```text
caligula/normalization/units.py
caligula/paths.py
caligula/validation/data_quality.py
```

Delete generic utility functions not used.

Acceptance gate:

- no utils.py above 150 lines
- no unrelated functions in one file
- no duplicate date parsers
- no duplicate unit converters

---

# Cleanup Pass 19: Type and Test Minimum

Add minimum tests for cleanup credibility.

Required tests:

```text
tests/test_no_stubs.py
tests/test_contracts.py
tests/test_point_in_time.py
tests/test_scoring.py
tests/test_backtest_metrics.py
tests/test_reserve_tv.py
```

Commands:

```bash
pytest -q
ruff check .
python -m caligula.validation.no_stub_scan
```

Acceptance gate:

- tests pass
- lint passes
- stub scan passes
- no import errors
- no skipped tests without reason

---

# Cleanup Pass 20: Build One Command Surface

Create one Makefile.

```makefile
.PHONY: clean validate test build-public run-all

clean:
	python -m caligula.validation.no_stub_scan
	ruff check . --fix
	ruff format .

validate:
	python -m caligula.validation.data_quality
	python -m caligula.validation.point_in_time
	python -m caligula.validation.parity
	python -m caligula.validation.no_stub_scan

test:
	pytest -q

build-public:
	python -m caligula.backtest.performance_ledger
	python -m caligula.valuation.eog_dcf
	python -m caligula.exports.website_public

run-all:
	python -m caligula.ingestion.filing_index
	python -m caligula.ingestion.extraction
	python -m caligula.normalization.reserve_mapping
	python -m caligula.scoring.rankings
	python -m caligula.backtest.performance_ledger
	python -m caligula.valuation.eog_dcf
	python -m caligula.exports.website_public
	$(MAKE) validate
	$(MAKE) test
```

Acceptance gate:

One command must regenerate public outputs:

```bash
make run-all
```

If this fails, the project is not clean.

---

# Required Final Cleanup Report

Generate:

```text
outputs/tables/cleanup_report.csv
outputs/memos/CODEBASE_CLEANUP_REPORT.md
```

CSV columns:

```text
category
files_deleted
files_archived
files_merged
stubs_removed
placeholders_removed
duplicate_paths_removed
hardcoded_metrics_removed
unused_dependencies_removed
validation_status
```

Markdown report sections:

```text
# Codebase Cleanup Report

## Summary
## Files Deleted
## Files Archived
## Duplicate Paths Removed
## Stubs Removed
## Hardcoded Metrics Removed
## Canonical Pipelines Preserved
## Remaining Allowed Exceptions
## Validation Results
## Next Required Cleanup
```

No vague language.

---

# Non-Negotiable Gates

The cleanup is incomplete unless all pass.

```bash
make clean
make validate
make test
make run-all
```

Also pass:

```bash
rg "TODO|FIXME|placeholder|dummy|mock|fake|coming soon|NotImplementedError" caligula app src components pages lib
```

Expected result:

```text
no matches
```

Also pass:

```bash
rg "final_final|main2|new_model|better_model|scratch|temp|manual|copy" .
```

Expected result:

```text
no live production matches
```

Also pass:

```bash
rg "141.22|149.60|8.77|5.9%|June 10, 2026" app src components pages lib
```

Expected result:

```text
no hardcoded production metrics
```

These values may appear only in:

```text
docs/archive/
outputs/tables/
outputs/memos/
```

---

# Implementation Instructions For Antigravity

Use this cleanup strategy.

1. Build inventory first.
2. Identify live execution paths.
3. Delete dead files aggressively.
4. Archive research history separately.
5. Replace stubs with real implementations or remove callers.
6. Remove hardcoded public metrics.
7. Create canonical contracts.
8. Route website through public JSON only.
9. Add validation gates.
10. Run tests after every major deletion batch.

Never create placeholder replacements.

If implementation is missing, choose one:

- implement fully now
- delete the caller
- archive the feature

Do not leave partial code.

---

# Definition Of Done

The cleaned Caligula codebase must satisfy this:

A reviewer can follow the project from raw filing to public website number without encountering fake data, duplicate formulas, placeholder logic, or unexplained dead branches.

A recruiter can inspect the repository without seeing vibe-coded clutter.

An investment professional can see which numbers are generated, which are sourced, which are audited, and which are excluded.

A future model upgrade can add features without fighting old scaffolding.

That is the desired state.
