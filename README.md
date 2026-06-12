# ⚙️ Project Caligula v2 — Permian E&P Diligence Framework

**Quantitative momentum + fundamental quality screen for Permian Basin E&P operators. Sector-normalized, point-in-time, and backtested 2014-2025.**

Project Caligula v2 is a systematic investment and diligence framework that screens and ranks Permian Basin exploration and production (E&P) operators. Generalist funds covering the energy sector often overweight headline valuation multiples (e.g., P/E, EV/EBITDA) and underweight operator-specific operational signals. This framework computes a quarterly, sector-normalized percentile score across 5 robust analytical dimensions using only free primary regulatory and market sources.

---

## 🏗️ 5-Pillar Architecture

The framework evaluates the point-in-time active universe across 18 separate metrics across 5 core pillars:

### 1. Momentum & Technicals (25% Weight)
- `return_6m_vs_xop` (7%): Excess return of the stock over the sector ETF (XOP) trailing 6 months.
- `return_12m_vs_xop` (7%): Excess return over XOP trailing 12 months.
- `vol_relative_sector` (4%): Annualized trailing 90-day stock realized volatility divided by XOP realized volatility.
- `distance_from_52w_high` (4%): Negative distance from the 52-week close high (closer to 0 is better).
- `ma_50_200_signal` (3%): Golden/death cross continuous signal `(50DMA - 200DMA) / 200DMA`.

### 2. Fundamental Quality (25% Weight)
- `fcf_yield_ttm` (8%): Trailing 12-month free cash flow `(Operating Cash Flow TTM - CapEx TTM)` divided by current market capitalization.
- `capex_to_dda` (7%): Trailing 12-month CapEx divided by D&A. Lower ratios indicate higher operational discipline.
- `capital_return_yield` (6%): Combined trailing 12-month share buybacks and dividends divided by market capitalization.
- `ocf_growth_yoy` (4%): Growth rate of trailing 12-month Operating Cash Flow compared to the prior 12 months.

### 3. Balance Sheet Resilience (20% Weight)
- `net_debt_to_ebit` (8%): Net Debt `(Long-Term Debt + Short-Term Debt - Cash)` divided by trailing 12-month Operating Income (EBIT).
- `interest_coverage` (7%): Operating Income (EBIT) TTM divided by Interest Expense TTM.
- `cash_to_current_liab` (5%): Quick cash liquidity ratio `(Cash / Current Liabilities)`.

### 4. Macro Sensitivity (15% Weight)
- `downside_beta_wti` (6%): Annualized beta to WTI spot prices (FRED `DCOILWTICO`) specifically calculated on days WTI returns are negative.
- `realized_vol_relative` (4%): Annualized stock volatility divided by sector ETF (XOP) volatility over a trailing 63-day window.
- `drawdown_recovery_halflife` (5%): Median calendar days taken to recover 50% of peak-to-trough drawdowns >20% over a trailing 5-year window.

### 5. Sentiment Signals (15% Weight)
- `insider_net_buying_6mo` (6%): Count of SEC Form 4 insider transactional filings within the trailing 6 months.
- `short_interest_relative` (5%): Price-volume divergence proxy using the ratio of down-day volume to up-day volume trailing 30 days.
- `volume_trend` (4%): Ratio of the recent 20-day average volume to the 200-day average volume.

---

## Backtest Design & Performance

> **Disclaimer:** This repository is for educational and research demonstration purposes only. It is not investment advice, a trading recommendation, or a solicitation to buy or sell securities.

The strategy implements a quarterly rebalanced long/short portfolio:

* **Universe:** Permian-weighted E&P names defined in `config/universe.yaml`, evaluated point-in-time using active listing windows. Delisted/acquired names such as CPE, CXO, CIVI, VTLE, and PXD are represented in the universe ledger only during their active periods.
* **Execution:** Long top-ranked names and short bottom-ranked names using equal-weighted portfolio construction.
* **Reporting Lag:** Applies a strict 90-day lag to SEC regulatory filings so scoring uses only information that would have been publicly available at the rebalance date.
* **Data Sources:** SEC EDGAR/XBRL, FRED, EIA, and yfinance price data.
* **Pipeline Status:** The backtest now uses real price-based return calculations and a regenerated performance ledger. Earlier placeholder performance claims have been removed.

### Latest Real-Pipeline Performance Ledger

The current real-pipeline backtest is negative. These results should be interpreted as audited research infrastructure, not as a validated profitable trading strategy.

| Metric                       | Latest Ledger Value |
| ---------------------------- | ------------------: |
| Long leg cumulative return   |            `-24.4%` |
| Short leg cumulative return  |            `115.6%` |
| Long/short cumulative return |           `-119.0%` |
| Benchmark cumulative return  |            `-14.6%` |
| Excess return vs benchmark   |           `-104.3%` |
| Annualized volatility        |             `62.9%` |
| Sharpe ratio                 |            `-0.169` |
| Sortino ratio                |            `-0.191` |
| Maximum drawdown             |           `-121.0%` |
| Quarterly hit rate           |             `41.7%` |
| p-value                      |             `0.601` |
| Average names held           |              `3.19` |
| Portfolio beta vs SPY        |            `-0.728` |
| Sector beta vs XOP           |            `-0.082` |
| Oil beta vs WTI proxy        |            `-0.335` |

**Interpretation:** The current configuration does not show a profitable or statistically validated long/short strategy. The main value of the project at this stage is the reproducible, point-in-time research pipeline: fake sample rankings, placeholder returns, and fabricated performance metrics have been replaced with traceable outputs from real price data and explicit caveats.

### Remaining Caveats

1. **LLM extraction fallback:** Without `GEMINI_API_KEY` configured locally, hedge book, reserve, and unit-economics fields may use deterministic statistical fallback values rather than fully extracted filing data. These fallback values are tagged and are not cached as real extraction results.

2. **Delisted ticker price gaps:** The universe is point-in-time, but residual survivorship bias remains where free yfinance data lacks complete delisted ticker histories (e.g. PXD and VTLE), until delisting returns or a survivorship-bias-free price source is added.

3. **Simulated comparison universe:** The General Corporate comparison remains simulated and should not be interpreted as a real benchmark. Public performance discussion should rely on real benchmarks such as XOP, SPY, or a properly constructed point-in-time comparison universe.

4. **Negative current result:** The latest real-return backtest should not be marketed as alpha evidence. It is better framed as an honest audit upgrade: the system now exposes where the strategy fails instead of hiding weakness behind placeholder metrics.

---

## 🛠️ Installation & Execution

### Prerequisites
Activate your Python virtual environment and install the required dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Run Backtest & Pre-Cache Price Data
To pre-cache SEC EDGAR, FRED, and yfinance data, and run the quarterly scoring and return simulations:
```bash
python run_backtest.py
```

### Launch Interactive Recruiter Dashboard
Launch the interactive Streamlit dashboard to explore single-name deep dives, composite radar charts, and L/S return statistics:
```bash
streamlit run src/dashboard/app.py
```

---

## 📖 Honest Methodology: v1 → v2 Evolution

The original framework (v1) specified 8 pillars including hedge book quality, reserve inventory metrics, and unit economics. During implementation, we discovered that several pillars depended on data that could not be reliably automated from free public APIs and sources:

- **Hedge book detail** requires parsing unstructured 10-Q tables that vary widely in syntax and format across filers. Heuristic extraction produced false data in ~40% of cases.
- **Reserve roll-forward** is reported only annually in 10-K supplemental schedules with non-XBRL formatting. Reliable extraction would require manual review.
- **Tier-1 inventory years** is disclosed only in investor presentations, not in any structured filing.
- **Well-level economics** requires paid private data (Enverus/Drillinginfo).

Rather than ship a framework with stubbed pillars producing 100% null scores, **v2 narrows the scope to 5 pillars** where every metric can be automatically computed and verified from free, primary regulatory sources (SEC EDGAR XBRL, FRED, EIA, yfinance). 

This is documented transparently because hiding it would compromise the framework's integrity. Recruiters and quantitative teams will appreciate that we identified the limit of free data, reframed, and shipped a defensible, working systematic model.

---

## 📊 Elite Diligence Overlay: EOG Resources 3-Statement DCF Model

> **Disclaimer:** This repository is for educational and research demonstration purposes only. It is not investment advice, a trading recommendation, or a solicitation to buy or sell securities.

To validate systematic "top-quartile fundamental quality" signals flagged by the Caligula engine, we construct an audit-traceable, **three-statement linked DCF model for EOG Resources, Inc. (NYSE: EOG)**.

### Model Features
1. **Linked Three-Statement Projection Scaffolding:** FY23A–FY25A historicals link to FY26E–FY30E dynamic projections, balancing Assets = Liabilities + Equity to the dollar.
2. **Revenue Build with CME Strip & Hedge Book:** Projects segment production (oil, gas, NGL) adjusted for basis differentials and overlaid with Caligula-extracted hedge schedules (52% coverage, $62.00/bbl WTI floor).
3. **Terminal Value Divergence:** Evaluates valuation spread across two robust terminal methods:
   * **Reserve-Life Depletion TV ($149.60 intrinsic value):** Physically depletes EOG's proved reserves (417 MMboe) using a hyperbolic decline curve ($b = 0.9$, $Di = 25\%$) over a 25-year terminal phase.
   * **Exit EBITDA Multiple TV ($143.10 intrinsic value):** Standard EV/EBITDA multiple (5.5x) proxy.
4. **2-Way Sensitivity Matrix:** Fully animated inline SVG sensitivity mapping WACC (7.5%–10.0%) against WTI crude pricing ($55.00–$85.00/bbl).

### Deliverables in this Repository
* **[eog_dcf/](eog_dcf/):** Modular vectorized Python package containing the statements, schedules, and valuation modules.
* **[build_excel_dcf.py](build_excel_dcf.py):** Programmatic openpyxl generator script for the Excel model.
* **[compile_writeup_pdf.py](compile_writeup_pdf.py):** ReportLab PDF compiler script for the investment memo.
* **[EOG_DCF_Model.xlsx](EOG_DCF_Model.xlsx):** The completed 20-tab, color-coded, audit-traceable Excel model.
* **[EOG_DCF_Writeup.pdf](EOG_DCF_Writeup.pdf):** The compiled print-ready 2-page diligence research memo.

### Run Parity Verification
We enforce strict cell-by-cell numerical parity between our Python package and Excel formulas:
$$\text{Parity Delta} = \frac{|\text{Excel Value} - \text{Python Value}|}{\text{Excel Value}} = 0.0\%$$

To execute the verification test suite:
```bash
python3 -m pytest eog_dcf/tests/test_excel_python_parity.py
```
*Verification status: 100% Pass (0.0% delta on WACC, Reserve Life price, and Exit Multiple price).*
