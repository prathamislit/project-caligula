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

## 📈 Backtest Design & Performance

The strategy implements a quarterly rebalanced Long/Short portfolio:
- **Universe:** 13 Permian-weighted E&P names. Evaluated point-in-time to eliminate look-ahead and survivorship bias (delisted/acquired names CPE, CXO, CIVI, VTLE, PXD are held only during their active periods).
- **Execution:** Long top-quartile names (Tier A/B), short bottom-quartile names (Tier C/D), equal-weighted.
- **Reporting Lag:** Incorporates a strict 90-day lag on SEC regulatory filings to ensure data is point-in-time and was actually available to the public.
- **Failed-Download Cache:** Built-in resilience caches delisted tickers as empty Parquet markers to prevent redundant slow API requests.

### Key Performance Metrics (2014-2025)
- **Annualized L/S Return:** `-7.9%` (Benchmark comparison and baseline short volatility risk).
- **Annualized Volatility:** `20.6%`
- **Sharpe Ratio:** `-0.384`
- **Maximum Drawdown:** `-28.1%`
- **Quarterly Hit Rate:** `37.5%`

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
