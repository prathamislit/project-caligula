# CALIGULA_FIX_IMPLEMENTATION_MDG.md

## Purpose

Upgrade Caligula from a polished undergraduate project into a defensible quantamental research system.

Primary goal:

> Remove credibility risk from AI extraction, backtesting, valuation dating, and reserve-life terminal value methodology.

This file is written to be pasted into Antigravity or Claude Code.

Do not treat this as optional cleanup.
These fixes are priority infrastructure.

---

# 0. Operating rules

## Non-negotiable rules

1. Do not invent numbers.
2. Do not future-date valuation data.
3. Do not display unsourced extracted values.
4. Do not claim backtest validity without audit records.
5. Do not keep broken methodology for aesthetics.
6. Do not hide failed extractions.
7. Do not overwrite raw extraction evidence.
8. Every derived metric must trace back to source filings or market data.

## Build priority

Rank fixes in this order:

1. AI extraction audit trail
2. Backtest audit example
3. Performance ledger
4. Valuation date and market timestamp hygiene
5. Point-in-time universe ledger
6. Pillar methodology table
7. Reserve bucket terminal value
8. Website display updates
9. Memo language cleanup
10. Repo documentation

---

# 1. Biggest Problem 1: AI extraction model risk

## Problem

Caligula uses AI extraction from SEC filings.
That creates model risk.

Current weakness:

- No accession number shown
- No filing date shown
- No source table location shown
- No raw extracted text shown
- No Gemini prompt version shown
- No confidence score shown
- No human override flag shown
- No audit hash shown
- No failed extraction rate shown
- No restatement handling shown

This is the highest-priority credibility problem.

## Required fix

Build a complete Extraction Audit Ledger.

This ledger must let a reviewer trace every model input back to an SEC filing.

---

## 1.1 Create file structure

Create these files:

```bash
mkdir -p data/audit
mkdir -p data/raw_filings
mkdir -p data/extracted
mkdir -p data/validation
mkdir -p docs/methodology
mkdir -p src/caligula/extraction
mkdir -p src/caligula/validation
```

Create:

```text
data/audit/extraction_ledger.csv
data/audit/extraction_failures.csv
data/audit/restatement_log.csv
data/audit/prompt_version_log.csv
docs/methodology/AI_EXTRACTION_AUDIT_METHOD.md
src/caligula/extraction/schema.py
src/caligula/extraction/hash_utils.py
src/caligula/validation/extraction_checks.py
```

---

## 1.2 Extraction ledger schema

Create `data/audit/extraction_ledger.csv` with this schema:

```csv
extraction_id,ticker,fiscal_year,fiscal_period,filing_type,accession_number,filing_date,period_end_date,accepted_datetime,source_url,source_document,source_page,source_section,source_table,row_label,column_label,metric_name,metric_category,extracted_value,reported_unit,normalized_value,normalized_unit,raw_extracted_text,model_provider,model_name,prompt_version,parser_version,confidence_score,human_reviewed,human_reviewer,human_override,override_reason,validation_status,validation_rule_failed,audit_hash,created_at,updated_at
```

Every extracted value must have one row.

Required fields:

- `extraction_id`
- `ticker`
- `fiscal_year`
- `filing_type`
- `accession_number`
- `filing_date`
- `accepted_datetime`
- `source_url`
- `source_section`
- `source_table`
- `metric_name`
- `extracted_value`
- `reported_unit`
- `normalized_value`
- `normalized_unit`
- `raw_extracted_text`
- `model_name`
- `prompt_version`
- `confidence_score`
- `human_reviewed`
- `human_override`
- `validation_status`
- `audit_hash`

Rows missing required fields must fail validation.

---

## 1.3 Failure ledger schema

Create `data/audit/extraction_failures.csv`:

```csv
failure_id,ticker,fiscal_year,fiscal_period,filing_type,accession_number,filing_date,metric_name,source_section,error_type,error_message,retry_count,resolved,resolution_method,human_review_required,created_at,updated_at
```

Use this file for:

- Missing filing
- Missing table
- Ambiguous unit
- AI parse failure
- Conflicting extracted values
- Validation failure
- Human unresolved item

Never delete failures.
Mark resolved when fixed.

---

## 1.4 Restatement log schema

Create `data/audit/restatement_log.csv`:

```csv
restatement_id,ticker,original_accession_number,amended_accession_number,original_filing_date,amended_filing_date,affected_fiscal_year,affected_metric,original_value,amended_value,delta,delta_pct,model_uses_amended_value,reason,created_at
```

Rules:

1. If a 10-K/A or 10-Q/A exists, log it.
2. If amended values change model inputs, record the replacement.
3. Preserve original values.
4. Do not silently overwrite original extracted records.

---

## 1.5 Prompt version log

Create `data/audit/prompt_version_log.csv`:

```csv
prompt_version,model_provider,model_name,prompt_file,prompt_hash,active_from,active_to,change_reason,created_by,created_at
```

Create prompt file:

```text
src/caligula/extraction/prompts/reserve_extraction_v1.txt
```

Minimum prompt instruction:

```text
Extract only values explicitly present in the source text.
Do not infer missing values.
Return null when unavailable.
Preserve units.
Quote the exact source text used.
Return confidence from 0.00 to 1.00.
Flag ambiguity.
```

---

## 1.6 Audit hash implementation

Create `src/caligula/extraction/hash_utils.py`:

```python
import hashlib
import json
from typing import Any, Dict


def canonical_json(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_audit_hash(payload: Dict[str, Any]) -> str:
    """Return SHA-256 hash for extraction audit payload."""
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
```

Hash these fields:

```text
ticker
fiscal_year
filing_type
accession_number
source_section
source_table
row_label
column_label
metric_name
extracted_value
reported_unit
raw_extracted_text
prompt_version
model_name
```

Purpose:

- prove value lineage
- detect silent edits
- enable audit replay

---

## 1.7 Extraction validation checks

Create `src/caligula/validation/extraction_checks.py`.

Implement these checks:

```python
REQUIRED_FIELDS = [
    "extraction_id",
    "ticker",
    "fiscal_year",
    "filing_type",
    "accession_number",
    "filing_date",
    "accepted_datetime",
    "source_url",
    "source_section",
    "metric_name",
    "extracted_value",
    "reported_unit",
    "normalized_value",
    "normalized_unit",
    "raw_extracted_text",
    "model_name",
    "prompt_version",
    "confidence_score",
    "human_reviewed",
    "human_override",
    "validation_status",
    "audit_hash",
]
```

Validation rules:

1. Required fields cannot be blank.
2. Confidence score must be between 0 and 1.
3. Reserve values cannot be negative.
4. Production values cannot be negative.
5. Reserve roll-forward must reconcile.
6. Units must be normalized.
7. Same ticker-year-metric cannot have duplicate active values.
8. Amended filing values must link to restatement log.
9. Raw text must contain the extracted value or explain normalization.
10. Any confidence below 0.85 requires human review.

Output validation summary to:

```text
data/validation/extraction_validation_summary.csv
```

Schema:

```csv
run_id,run_timestamp,total_records,passed_records,failed_records,warning_records,failed_extraction_rate,low_confidence_rate,human_review_rate,override_rate
```

---

# 2. Reserve item mapping

## Problem

Caligula should not merely extract total reserves.
It must map every reserve-related value into a standardized reserve schema.

Required reserve fields:

- filing year
- proved developed
- proved undeveloped
- total proved
- oil mix
- gas mix
- NGL mix
- standardized measure
- production
- extensions / discoveries
- revisions
- purchases / sales

## Required fix

Create a Reserve Fact Table.

---

## 2.1 Create reserve fact table

Create:

```text
data/extracted/reserve_fact_table.csv
```

Schema:

```csv
reserve_record_id,ticker,fiscal_year,filing_type,accession_number,filing_date,period_end_date,commodity,basin,reserve_category,measure_type,value,unit,normalized_value,normalized_unit,source_extraction_id,source_table,source_page,audit_hash
```

Allowed `commodity` values:

```text
oil
gas
ngl
boe
combined
```

Allowed `reserve_category` values:

```text
proved_developed
proved_undeveloped
total_proved
pdp
pdnp
pud
```

Allowed `measure_type` values:

```text
beginning_reserves
extensions_discoveries
revisions
improved_recovery
purchases
sales
production
ending_reserves
standardized_measure
future_net_cash_flows
future_income_taxes
future_development_costs
```

---

## 2.2 Reserve reconciliation rule

For each ticker-year-commodity:

```text
ending_reserves = beginning_reserves
                + extensions_discoveries
                + revisions
                + improved_recovery
                + purchases
                - sales
                - production
```

If reconciliation error exceeds 1.0%, flag it.

Create output:

```text
data/validation/reserve_reconciliation.csv
```

Schema:

```csv
ticker,fiscal_year,commodity,beginning_reserves,extensions_discoveries,revisions,improved_recovery,purchases,sales,production,calculated_ending_reserves,reported_ending_reserves,reconciliation_error,reconciliation_error_pct,status
```

Status values:

```text
pass
warning
fail
manual_review
```

---

## 2.3 Public website display

Add a visible table in the Caligula section:

Title:

```text
SEC Extraction Audit Snapshot
```

Columns:

```text
Metric
Value
```

Rows:

```text
Filings parsed
Extracted data points
Human-reviewed records
AI confidence median
Failed extraction rate
Reserve reconciliation pass rate
Amended filing adjustments
Prompt version
```

Add another table:

Title:

```text
Reserve Mapping Coverage
```

Rows:

```text
Proved developed
Proved undeveloped
Total proved
Oil / gas / NGL mix
Production
Extensions / discoveries
Revisions
Purchases / sales
Standardized measure
```

Each row should show:

```text
Covered / Partial / Missing
```

Do not show green status unless backed by validation files.

---

# 3. Biggest Problem 2: Backtest audit example

## Problem

Backtest credibility depends on point-in-time evidence.

The site claims point-in-time cutoff discipline.
But it needs one concrete audit example.

## Required fix

Add a Backtest Audit Example.

This should prove that one quarterly signal used only data available before the rebalance date.

---

## 3.1 Create audit file

Create:

```text
data/audit/backtest_audit_example.csv
```

Schema:

```csv
audit_id,ticker,signal_quarter,rebalance_date,filing_type,accession_number,filing_date,accepted_datetime,data_available_before_rebalance,metric_name,metric_value,score_used,rank_used,portfolio_bucket,execution_price_source,execution_price,return_start_date,return_end_date,holding_period_return,notes
```

Use EOG as first example.

Required example:

```text
Ticker: EOG
Signal quarter: choose one historical quarter with complete filing data
Portfolio bucket: top quartile or actual rank bucket
```

Do not use future data.
Do not use data filed after rebalance date.

---

## 3.2 Backtest audit narrative

Create:

```text
docs/methodology/BACKTEST_AUDIT_EXAMPLE.md
```

Include this structure:

```markdown
# Backtest Audit Example

## Objective
Show one complete point-in-time signal path.

## Example security
Ticker: EOG
Signal quarter: [quarter]
Rebalance date: [date]

## Filing availability
Filing type: [10-K / 10-Q]
Accession number: [accession]
Filing date: [date]
Accepted datetime: [datetime]

## Data cutoff rule
Only filings accepted before [rebalance timestamp] are eligible.

## Extracted metrics used
| Metric | Value | Source extraction ID | Filing accession |
|---|---:|---|---|

## Score construction
| Pillar | Score | Weight | Contribution |
|---|---:|---:|---:|

## Portfolio assignment
Rank: [x/n]
Bucket: [top quartile / middle / bottom quartile]

## Return measurement
Execution date: [date]
Execution price source: [source]
Return window: [start] to [end]
Holding-period return: [x%]

## Conclusion
This example confirms that the backtest used only data available before the rebalance date.
```

---

## 3.3 Website display

Add visible block:

```text
Backtest Audit Example
```

Show:

- ticker
- signal quarter
- filing accepted timestamp
- rebalance date
- data cutoff pass/fail
- rank
- bucket
- holding-period return

Add link:

```text
View audit example
```

---

# 4. Biggest Problem 3: Performance Ledger

## Problem

A performance chart is not enough.
Backtest output needs full return, statistical, portfolio, and realism metrics.

## Required fix

Create a visible Performance Ledger.

---

## 4.1 Create performance files

Create:

```text
data/backtest/performance_ledger.csv
data/backtest/quarterly_returns.csv
data/backtest/portfolio_holdings.csv
data/backtest/factor_exposures.csv
data/backtest/realism_costs.csv
docs/methodology/PERFORMANCE_LEDGER_METHOD.md
```

---

## 4.2 Performance ledger schema

Create `data/backtest/performance_ledger.csv`:

```csv
run_id,run_date,universe_version,signal_version,start_date,end_date,rebalance_frequency,long_return,short_return,long_short_return,benchmark_return,excess_return,cagr,annualized_volatility,sharpe,sortino,max_drawdown,calmar_ratio,spearman_ic,pearson_ic,ic_tstat,hit_rate,p_value,newey_west_tstat,bootstrap_ci_low,bootstrap_ci_high,turnover,average_names_held,concentration_hhi,beta,sector_beta,oil_beta,gas_beta,size_exposure,value_exposure,leverage_exposure,momentum_exposure,bid_ask_cost_bps,short_borrow_assumption_bps,slippage_bps,average_delay_after_filing_days,failed_extraction_rate,notes
```

---

## 4.3 Required metric definitions

Add these definitions to `docs/methodology/PERFORMANCE_LEDGER_METHOD.md`:

```markdown
# Performance Ledger Method

## Return metrics
Long return: total return of top-quartile portfolio.
Short return: total return of bottom-quartile short book.
Long-short return: long return minus short return.
Benchmark return: chosen E&P benchmark return.
Excess return: long-short return minus benchmark return where applicable.
CAGR: annualized geometric return.
Annualized volatility: standard deviation of periodic returns annualized.
Sharpe: annualized excess return divided by annualized volatility.
Sortino: annualized excess return divided by downside deviation.
Max drawdown: largest peak-to-trough decline.
Calmar ratio: CAGR divided by absolute max drawdown.

## Statistical metrics
Spearman IC: rank correlation between signal score and forward return.
Pearson IC: linear correlation between signal score and forward return.
IC t-stat: mean IC divided by standard error.
Hit rate: share of periods where top quartile outperformed bottom quartile.
p-value: significance test for IC or long-short return.
Newey-West adjusted t-stat: autocorrelation-adjusted t-stat.
Bootstrap confidence interval: resampled return confidence interval.

## Portfolio metrics
Turnover: half the absolute change in portfolio weights.
Average names held: average quarterly count of long and short names.
Concentration HHI: sum of squared portfolio weights.
Beta: regression beta versus broad equity benchmark.
Sector beta: regression beta versus E&P benchmark.
Oil beta: regression beta versus WTI return.
Gas beta: regression beta versus Henry Hub return.
Size exposure: correlation or regression exposure to market cap factor.
Value exposure: exposure to valuation factor.
Leverage exposure: exposure to debt/capital factor.
Momentum exposure: exposure to trailing return factor.

## Realism metrics
Bid-ask cost: assumed trading cost per rebalance.
Short borrow assumption: annualized short borrow cost.
Slippage: execution penalty assumption.
Delay after filing: days between filing availability and signal use.
Failed extraction rate: failed extracted records divided by attempted records.
```

---

## 4.4 Calculation requirements

Implement these calculations in Python.

Create:

```text
src/caligula/backtest/performance_metrics.py
```

Functions required:

```python
def calc_cagr(returns, periods_per_year): ...
def calc_annualized_volatility(returns, periods_per_year): ...
def calc_sharpe(returns, risk_free_rate, periods_per_year): ...
def calc_sortino(returns, risk_free_rate, periods_per_year): ...
def calc_max_drawdown(returns): ...
def calc_calmar(cagr, max_drawdown): ...
def calc_spearman_ic(scores, forward_returns): ...
def calc_pearson_ic(scores, forward_returns): ...
def calc_ic_tstat(ic_series): ...
def calc_hit_rate(long_returns, short_returns): ...
def calc_newey_west_tstat(return_series, lags=4): ...
def calc_bootstrap_ci(return_series, n_bootstrap=10000, ci=0.95): ...
def calc_turnover(weights_by_period): ...
def calc_hhi(weights): ...
def calc_beta(strategy_returns, benchmark_returns): ...
```

Do not display metrics until tests pass.

---

## 4.5 Website display

Add section:

```text
Performance Ledger
```

Use four tables.

### Return Metrics

Columns:

```text
Metric
Value
```

Rows:

```text
Long return
Short return
Long-short return
Benchmark return
Excess return
CAGR
Annualized volatility
Sharpe
Sortino
Max drawdown
Calmar ratio
```

### Statistical Metrics

Rows:

```text
Spearman IC
Pearson IC
IC t-stat
Hit rate
p-value
Newey-West t-stat
Bootstrap confidence interval
```

### Portfolio Metrics

Rows:

```text
Turnover
Average names held
Concentration
Beta
Sector beta
Oil beta
Gas beta
Size exposure
Value exposure
Leverage exposure
Momentum exposure
```

### Realism Metrics

Rows:

```text
Bid-ask cost
Short borrow assumption
Slippage
Delay after filing
Failed extraction rate
```

If a metric is not implemented, show:

```text
Not yet implemented
```

Do not leave blank cells.
Do not fake values.

---

# 5. Biggest Problem 4: Valuation date hygiene

## Problem

The EOG DCF uses a future valuation date.
This damages credibility.

## Required fix

No future-dated market data.

---

## 5.1 Replace valuation-date language

Find all instances of:

```text
Valuation Date: June 10, 2026
```

Replace with one of these two options.

Preferred option:

```text
Draft valuation date: June 10, 2026
Market data pulled as of: [ACTUAL_TIMESTAMP]
```

Better option:

```text
Valuation date: [ACTUAL_DATE]
Market data pulled as of: [ACTUAL_TIMESTAMP]
```

Use actual market-data timestamp.
Do not use future timestamp.

---

## 5.2 Add market data provenance

Create:

```text
data/valuation/market_data_snapshot.csv
```

Schema:

```csv
ticker,valuation_date,market_data_pulled_at,share_price,shares_outstanding,market_cap,net_debt,enterprise_value,source,source_url,notes
```

Every public valuation output must reference this file.

---

## 5.3 Add DCF input timestamp block

In EOG DCF memo and website, add:

```text
Valuation Data Snapshot
```

Show:

```text
Valuation date
Market data pulled at
Share price
Shares outstanding
Net debt
Enterprise value
Commodity strip timestamp
WACC input timestamp
```

If data was manually entered, say:

```text
Manual input; source retained in model notes
```

---

# 6. Biggest Problem 5: Reserve-life terminal value needs bucket logic

## Problem

A single reserve-life depletion curve is too blunt.

E&P reserves are not one homogeneous asset.
PDP, PDNP, and PUD have different risk, capex, timing, and decline behavior.

## Required fix

Build reserve-life TV using reserve buckets.

---

## 6.1 Create reserve bucket model

Create:

```text
data/valuation/reserve_bucket_terminal_value.csv
```

Schema:

```csv
ticker,valuation_date,reserve_bucket,commodity,starting_reserves_boe,risk_factor,initial_decline_rate,terminal_decline_rate,decline_exponent,development_capex_per_boe,loe_per_boe,transport_per_boe,production_tax_rate,realization_pct,price_deck,production_year,annual_production_boe,revenue,operating_costs,development_capex,taxes,fcff,discount_factor,pv_fcff
```

Allowed reserve buckets:

```text
PDP
PDNP
PUD
```

---

## 6.2 Required assumptions

Use these default conceptual rules unless better sourced values exist:

```text
PDP: lowest risk, existing production, no major development capex.
PDNP: medium risk, needs completion or connection capex.
PUD: highest risk, needs future drilling and development capex.
```

Never apply the same risk factor to all buckets.
Never apply the same capex profile to all buckets.

Suggested initial placeholders:

```text
PDP risk factor: 100%
PDNP risk factor: 85% to 95%
PUD risk factor: 60% to 85%
```

These must be clearly labeled as assumptions unless sourced.

---

## 6.3 Terminal value calculation

Calculate:

```text
Reserve Bucket TV = Σ PV(bucket-level annual FCFF)
```

Then:

```text
Total Reserve-Life TV = PDP PV + PDNP PV + PUD PV
```

Output:

```text
data/valuation/reserve_bucket_tv_summary.csv
```

Schema:

```csv
ticker,valuation_date,pdp_pv,pdnp_pv,pud_pv,total_reserve_life_tv,pdp_pct,pdnp_pct,pud_pct,notes
```

---

## 6.4 DCF memo update

Replace language implying one reserve curve with:

```text
Reserve-life terminal value is calculated using bucketed reserve economics.
PDP, PDNP, and PUD volumes are modeled separately to reflect different risk, decline, and development-capex profiles.
```

Add table:

```markdown
| Bucket | Risking | Decline assumption | Capex treatment | PV contribution |
|---|---:|---|---|---:|
| PDP | x% | x | x | x |
| PDNP | x% | x | x | x |
| PUD | x% | x | x | x |
```

---

# 7. Point-in-Time Universe Ledger

## Problem

A 2014-2026 backtest can suffer survivorship bias.

The project currently needs a visible point-in-time universe record.

## Required fix

Publish a Point-in-Time Universe Ledger.

---

## 7.1 Create universe files

Create:

```text
data/universe/point_in_time_universe.csv
data/universe/universe_changes.csv
docs/methodology/POINT_IN_TIME_UNIVERSE_METHOD.md
```

---

## 7.2 Universe ledger schema

Create `data/universe/point_in_time_universe.csv`:

```csv
universe_version,as_of_date,rebalance_quarter,ticker,company_name,eligible,inclusion_reason,exclusion_reason,listing_status,exchange,first_trade_date,last_trade_date,market_cap,adv_30d,liquidity_pass,market_cap_pass,filing_available,basin_classification,sector_classification,delisting_return_applied,mna_adjustment_applied,bankruptcy_flag,notes
```

---

## 7.3 Universe changes schema

Create `data/universe/universe_changes.csv`:

```csv
change_id,effective_date,ticker,company_name,change_type,reason,source,notes
```

Allowed change types:

```text
added
removed
ticker_change
merger
acquisition
bankruptcy
delisting
spin_off
classification_change
```

---

## 7.4 Universe methodology file

Create `docs/methodology/POINT_IN_TIME_UNIVERSE_METHOD.md`:

```markdown
# Point-in-Time Universe Method

## Objective
Prevent survivorship bias in the Caligula backtest.

## Universe rule
At each rebalance date, only companies that were investable and had eligible filing data before the rebalance cutoff may enter the ranking universe.

## Inclusion criteria
- U.S.-listed E&P company
- Sufficient public filing history
- Minimum market cap threshold
- Minimum liquidity threshold
- Relevant oil and gas operating exposure

## Exclusion criteria
- Not public at rebalance date
- Missing required filing data
- Insufficient liquidity
- Non-comparable business model
- Delisted before holding window without return treatment

## Survivorship control
Universe membership is reconstructed as of each rebalance date.
Current membership is not applied backward.

## Corporate actions
Mergers, bankruptcies, ticker changes, and delistings are logged separately.
```

---

# 8. Pillar Methodology Table

## Problem

Caligula has strong pillar names.
But reviewers need formulas.

## Required fix

Add a Pillar Methodology Table.

---

## 8.1 Create methodology table

Create:

```text
data/methodology/pillar_methodology.csv
```

Schema:

```csv
pillar_id,pillar_name,metric_name,raw_formula,direction,normalization,winsorization,missing_data_rule,weight,source_type,source_table,rebalance_lag,notes
```

Allowed direction:

```text
higher_is_better
lower_is_better
neutral
```

Example row:

```csv
P1,Hedge Book,NTM Hedge Floor Coverage,hedged_ntm_volume / expected_ntm_production,higher_is_better,z_score_by_quarter,5th_95th_percentile,sector_median_impute,12.5%,SEC filing hedge footnote,Derivative instruments table,filing_cutoff_plus_next_rebalance,
```

---

## 8.2 Public website table

Add visible section:

```text
Pillar Methodology
```

Columns:

```text
Pillar
Metric
Formula
Direction
Normalization
Weight
Source
```

Do not expose excessive code.
But expose enough to replicate logic.

---

## 8.3 Required pillar documentation

Create:

```text
docs/methodology/PILLAR_METHODOLOGY.md
```

Include:

```markdown
# Pillar Methodology

## Composite score
Composite Score = Σ(normalized metric score × pillar weight)

## Normalization
Scores are normalized within each rebalance quarter.

## Missing data
Missing values are handled using the declared missing-data rule.
No missing value is silently replaced.

## Directionality
Each metric explicitly defines whether higher or lower values are better.

## Point-in-time rule
Only values available before the rebalance cutoff are eligible.
```

---

# 9. Investment conclusion discipline

## Problem

A 5.9% DCF upside is too thin for a strong Long call.

## Required fix

Replace aggressive recommendation language.

---

## 9.1 Rating framework

Add:

```text
data/valuation/rating_framework.csv
```

Schema:

```csv
rating,min_upside,max_upside,interpretation
Avoid,-100,0,Intrinsic value below market price
Watchlist,0,10,Undervaluation too small for decisive long call
Constructive,10,20,Moderate valuation support
Long,20,1000,Strong valuation support
```

---

## 9.2 Replace conclusion language

Replace:

```text
Recommend Long
```

With:

```text
Watchlist / Mildly Undervalued
```

Unless upside exceeds the rating threshold.

Use this exact conclusion logic:

```text
Caligula confirms EOG's quality profile, but the DCF spread is modest.
The signal supports watchlist inclusion, not an aggressive standalone long call.
A stronger long thesis requires a wider valuation discount, stronger commodity setup, or clearer reserve-replacement advantage.
```

---

# 10. Website and memo credibility cleanup

## Required wording changes

Replace:

```text
replicating EOG’s ultra-low-cost historical structure perfectly
```

With:

```text
calibrated to EOG’s historical low-cost operating structure
```

Replace:

```text
CONFIDENTIAL
```

With:

```text
Public Research Draft
```

Replace inflated author labels with:

```text
Author
Researcher
Project Lead
Undergraduate Research
```

Fix typos:

```text
dilutive Conclusion -> Dilutive Conclusion or remove if irrelevant
22-Way -> 2-Way
```

Avoid these claims unless proven:

```text
institutional-grade
alpha-generating
validated investment strategy
market-beating
production-ready
AI hedge fund model
perfectly
```

---

# 11. Acceptance criteria

Do not mark project upgraded until all conditions pass.

## 11.1 AI extraction audit pass

Required:

- `extraction_ledger.csv` exists
- every extracted metric has accession number
- every extracted metric has filing date
- every extracted metric has source section/table
- every extracted metric has raw extracted text
- every extracted metric has prompt version
- every extracted metric has confidence score
- every extracted metric has audit hash
- failed extraction rate is calculated
- low-confidence rows are flagged
- restatements are logged

## 11.2 Reserve mapping pass

Required:

- reserve fact table exists
- proved developed mapped
- proved undeveloped mapped
- total proved mapped
- oil/gas/NGL mix mapped where available
- production mapped
- reserve roll-forward reconciliation exists
- standardized measure mapped where available

## 11.3 Backtest audit pass

Required:

- one EOG audit example exists
- accession number shown
- filing accepted timestamp shown
- rebalance date shown
- data cutoff pass/fail shown
- score contribution shown
- rank shown
- bucket shown
- holding-period return shown

## 11.4 Performance ledger pass

Required:

- return metrics calculated or labeled not implemented
- statistical metrics calculated or labeled not implemented
- portfolio metrics calculated or labeled not implemented
- realism metrics calculated or labeled not implemented
- no blank public cells
- no fake placeholder values

## 11.5 Valuation hygiene pass

Required:

- no future valuation date unless labeled draft
- market data timestamp shown
- share price source shown
- commodity strip timestamp shown
- WACC input timestamp shown

## 11.6 Reserve TV pass

Required:

- PDP modeled separately
- PDNP modeled separately
- PUD modeled separately
- risk factors shown
- capex treatment shown
- PV contribution shown

---

# 12. Final desired website state

The Caligula section should contain these visible blocks:

1. Project thesis
2. Universe and data coverage
3. AI extraction audit snapshot
4. Reserve mapping coverage
5. Pillar methodology table
6. Point-in-time universe summary
7. Backtest audit example
8. Performance ledger
9. EOG DCF valuation snapshot
10. Reserve bucket terminal value summary
11. Limitations and controls
12. Downloadable methodology appendix

---

# 13. Final desired repo state

Expected tree:

```text
caligula/
  data/
    audit/
      extraction_ledger.csv
      extraction_failures.csv
      restatement_log.csv
      prompt_version_log.csv
      backtest_audit_example.csv
    backtest/
      performance_ledger.csv
      quarterly_returns.csv
      portfolio_holdings.csv
      factor_exposures.csv
      realism_costs.csv
    extracted/
      reserve_fact_table.csv
    methodology/
      pillar_methodology.csv
    universe/
      point_in_time_universe.csv
      universe_changes.csv
    validation/
      extraction_validation_summary.csv
      reserve_reconciliation.csv
    valuation/
      market_data_snapshot.csv
      reserve_bucket_terminal_value.csv
      reserve_bucket_tv_summary.csv
      rating_framework.csv
  docs/
    methodology/
      AI_EXTRACTION_AUDIT_METHOD.md
      BACKTEST_AUDIT_EXAMPLE.md
      PERFORMANCE_LEDGER_METHOD.md
      POINT_IN_TIME_UNIVERSE_METHOD.md
      PILLAR_METHODOLOGY.md
  src/
    caligula/
      extraction/
        schema.py
        hash_utils.py
        prompts/
          reserve_extraction_v1.txt
      validation/
        extraction_checks.py
      backtest/
        performance_metrics.py
```

---

# 14. Implementation order

Execute in this order:

## Phase 1 — Audit backbone

1. Create all folders.
2. Create ledger schemas.
3. Create hash utility.
4. Create extraction validation script.
5. Create prompt version log.
6. Create AI extraction methodology doc.

Gate:

```text
A sample extraction row can be validated and hashed.
```

## Phase 2 — Reserve mapping

1. Create reserve fact table.
2. Map reserve values into standardized fields.
3. Implement reserve reconciliation.
4. Create reserve coverage table.

Gate:

```text
At least one EOG fiscal year reconciles or flags clearly.
```

## Phase 3 — Backtest trust layer

1. Create point-in-time universe ledger.
2. Create backtest audit example.
3. Create performance ledger.
4. Implement performance metric functions.

Gate:

```text
One EOG backtest quarter is fully auditable.
```

## Phase 4 — DCF credibility layer

1. Fix valuation date language.
2. Create market data snapshot.
3. Create reserve bucket TV files.
4. Replace aggressive recommendation language.
5. Add rating framework.

Gate:

```text
No future-dated market data appears publicly.
```

## Phase 5 — Public presentation

1. Add website sections.
2. Add methodology links.
3. Remove overclaiming language.
4. Fix typos.
5. Ensure all missing metrics say `Not yet implemented`.

Gate:

```text
A skeptical reviewer can trace each major claim.
```

---

# 15. Final instruction to Antigravity

Implement the above as infrastructure first.
Do not optimize styling first.
Do not change the thesis.
Do not invent values.
Do not fake completed metrics.

Where data is unavailable, show:

```text
Not yet implemented
```

or:

```text
Pending source verification
```

The final project should look less flashy and more auditable.
Credibility beats aesthetics.
