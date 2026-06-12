"""Narrative Generation Module.
Translates complex scoring matrices and financials into institutional-grade,
compliance-safe, and context-aware business storytelling (Bloomberg-style).
"""
import os
import requests
import json
import numpy as np

# Ensure parents directories exist
os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)

# Pillar translations helper for general corporate tickers
def get_general_narratives(data: dict) -> dict:
    """Generates an institutional-grade, objective translation of general corporate financial scores.
    
    Adheres strictly to the 'Objective Translation' rule (factual percentiles, no advice/opinion).
    """
    ticker = data.get("ticker", "ticker").upper()
    metrics = data.get("raw_metrics", {})
    
    # 1. Unit Economics
    ue_score = data.get("unit_economics_score", 0.5)
    gm = metrics.get("gross_margin")
    om = metrics.get("operating_margin")
    gm_str = f"{gm*100:.1f}%" if gm is not None else "N/A"
    om_str = f"{om*100:.1f}%" if om is not None else "N/A"
    
    if ue_score >= 0.70:
        ue_text = (
            f"Demonstrates elite cost-of-goods management with a gross margin of {gm_str} and operating margin of {om_str}. "
            "This top-tier structural pricing power indicates substantial competitive barriers and strong operational efficiency."
        )
    elif ue_score >= 0.50:
        ue_text = (
            f"Maintains a sustainable cost profile with a gross margin of {gm_str} and operating margin of {om_str}. "
            "These margins align with competitive sector norms, indicating moderate pricing power under standard conditions."
        )
    else:
        ue_text = (
            f"Under pressure from elevated cost of sales, resulting in a gross margin of {gm_str} and operating margin of {om_str}. "
            "This below-average profit profile points to high capital sensitivity or intense industry pricing competition."
        )

    # 2. Capital Discipline
    cd_score = data.get("capital_discipline_score", 0.5)
    roa = metrics.get("roa")
    fcf_yield = metrics.get("fcf_yield")
    roa_str = f"{roa*100:.1f}%" if roa is not None else "N/A"
    fcf_str = f"{fcf_yield*100:.1f}%" if fcf_yield is not None else "N/A"
    
    if cd_score >= 0.70:
        cd_text = (
            f"Reflects exceptional capital allocation efficiency, yielding an ROA of {roa_str} and FCF yield of {fcf_str}. "
            "This performance indicates superior cash conversion, asset productivity, and disciplined organic growth reinvestment."
        )
    elif cd_score >= 0.50:
        cd_text = (
            f"Maintains an adequate capital allocation framework, with an ROA of {roa_str} and FCF yield of {fcf_str}. "
            "This indicates consistent asset utilization that successfully satisfies structural financing and capital costs."
        )
    else:
        cd_text = (
            f"Indicates capital utilization friction, marked by a depressed ROA of {roa_str} and FCF yield of {fcf_str}. "
            "This compression highlights structural inefficiencies, low asset turnover, or sub-par conversion of sales to free cash."
        )

    # 3. Balance Sheet Resilience
    bs_score = data.get("balance_sheet_score", 0.5)
    de = metrics.get("debt_ebitda")
    cr = metrics.get("current_ratio")
    de_str = f"{de:.2f}x" if de is not None else "N/A"
    cr_str = f"{cr:.2f}x" if cr is not None else "N/A"
    
    if bs_score >= 0.70:
        bs_text = (
            f"Possesses a fortress balance sheet characterized by a highly conservative Net Debt/EBITDA of {de_str} "
            f"and a robust current ratio of {cr_str}. This positioning indicates a strong defensive cushion against systemic credit shocks."
        )
    elif bs_score >= 0.50:
        bs_text = (
            f"Leverage is moderate, with a Net Debt/EBITDA of {de_str} and a current ratio of {cr_str}. "
            "This liquidity profile aligns with standard industry credit ratings, showing comfortable debt service under normal conditions."
        )
    else:
        bs_text = (
            f"Displays an elevated debt structure, with a Net Debt/EBITDA of {de_str} and a current ratio of {cr_str}. "
            "This leveraged posture increases systemic sensitivity to high-interest credit cycles and reduces balance sheet flexibility."
        )

    # 4. Risk Mitigation & Hedging
    h_score = data.get("hedge_book_score", 0.5)
    qr = metrics.get("quick_ratio")
    cd_ratio = metrics.get("cash_debt")
    qr_str = f"{qr:.2f}x" if qr is not None else "N/A"
    cd_str = f"{cd_ratio*100:.1f}%" if cd_ratio is not None else "N/A"
    
    if h_score >= 0.70:
        h_text = (
            f"Maintains superior liquid buffers with a quick ratio of {qr_str} and a cash-to-debt cover of {cd_str}. "
            "This liquidity positioning provides substantial strategic protection against localized business interruptions."
        )
    elif h_score >= 0.50:
        h_text = (
            f"Carries adequate financial cover, sustaining a quick ratio of {qr_str} and cash-to-debt of {cd_str}. "
            "This baseline liquidity cover aligns with median corporate benchmarks, securing intermediate obligations."
        )
    else:
        h_text = (
            f"Maintains a thin liquid cushion with a quick ratio of {qr_str} and cash-to-debt of {cd_str}. "
            "This minimal reserve coverage increases vulnerability to localized working capital stress or sudden cash drawdowns."
        )

    # 5. Growth & Asset Lifespan
    r_score = data.get("reserves_score", 0.5)
    rev_growth = metrics.get("revenue_growth")
    earn_growth = metrics.get("earnings_growth")
    rg_str = f"{rev_growth*100:.1f}%" if rev_growth is not None else "N/A"
    eg_str = f"{earn_growth*100:.1f}%" if earn_growth is not None else "N/A"
    
    if r_score >= 0.70:
        r_text = (
            f"Exhibits stellar organic expansion, sustaining a top-line growth rate of {rg_str} and earnings trajectory of {eg_str}. "
            "This high-velocity growth demonstrates strong market demand capture and expanding competitive footprints."
        )
    elif r_score >= 0.50:
        r_text = (
            f"Displays stable, moderate growth, with revenue expansion at {rg_str} and earnings growth at {eg_str}. "
            "This profile demonstrates mature market-share retention aligned with long-term macroeconomic trends."
        )
    else:
        r_text = (
            f"Reflects structural stagnation or organic contraction, with revenue growth at {rg_str} and earnings at {eg_str}. "
            "This compression highlights sector saturation, cyclical downturns, or competitive displacement."
        )

    # 6. Operational Momentum
    op_score = data.get("operational_score", 0.5)
    roe = metrics.get("roe")
    peg = metrics.get("peg_ratio")
    roe_str = f"{roe*100:.1f}%" if roe is not None else "N/A"
    peg_str = f"{peg:.2f}x" if peg is not None else "N/A"
    
    if op_score >= 0.70:
        op_text = (
            f"Exhibits superior equity efficiency with an ROE of {roe_str} and a highly attractive growth-adjusted valuation PEG of {peg_str}. "
            "This indicates strong pricing discipline and high shareholder capital optimization."
        )
    elif op_score >= 0.50:
        op_text = (
            f"Sustains reasonable efficiency metrics, generating an ROE of {roe_str} and a PEG ratio of {peg_str}. "
            "This indicates standard operational execution, tracking intermediate equity returns."
        )
    else:
        op_text = (
            f"Exhibits compressed operational efficiency, with an ROE of {roe_str} and a premium PEG of {peg_str}. "
            "This lag reflects asset under-utilization, bloated corporate overhead, or over-valued equity relative to core earnings growth."
        )

    # 7. Sentiment Signals
    s_score = data.get("sentiment_score", 0.5)
    sp = metrics.get("short_pct")
    sr = metrics.get("short_ratio")
    sp_str = f"{sp*100:.2f}%" if sp is not None else "N/A"
    sr_str = f"{sr:.2f}x" if sr is not None else "N/A"
    
    if s_score >= 0.70:
        s_text = (
            f"Enjoys strong market and institutional trust, characterized by a minimal short float of {sp_str} "
            f"and short cover ratio of {sr_str}. This positioning indicates low market skepticism and high shareholder stability."
        )
    elif s_score >= 0.50:
        s_text = (
            f"Sustains standard market sentiment, with a short interest float of {sp_str} and a short ratio of {sr_str}. "
            "This neutral position reflects balanced market expectations without heavy speculative short pressure."
        )
    else:
        s_text = (
            f"Subject to elevated market skepticism, marked by a short interest float of {sp_str} "
            f"and short ratio of {sr_str}. This positioning indicates bearish hedging activity or active structural short campaigns."
        )

    # 8. Macro Sensitivity
    m_score = data.get("macro_sensitivity_score", 0.5)
    beta = metrics.get("beta")
    beta_str = f"{beta:.2f}" if beta is not None else "N/A"
    
    if m_score >= 0.70:
        m_text = (
            f"Presents a resilient low-beta profile of {beta_str}, which significantly insulates the company "
            "from systemic S&P 500 swings. This defensive positioning is highly attractive for institutional risk-off allocations."
        )
    elif m_score >= 0.50:
        m_text = (
            f"Carries a market-neutral beta profile of {beta_str}, moving in tandem with major benchmarks. "
            "This profile aligns with systemic equity risk, offering standard beta exposure."
        )
    else:
        m_text = (
            f"Exhibits a high-beta posture of {beta_str}, exposing its equity to amplified market volatility. "
            "This sensitivity increases drawdown risk during broader economic corrections and index-wide sell-offs."
        )

    # Cohesive Strategic Summary
    score = data.get("caligula_score", 0.5)
    tier = data.get("tier", "C")
    
    if score >= 0.70:
        summary = (
            f"{ticker} displays an elite, Tier {tier} quantamental quality profile (Score: {score:.3f}). "
            "The company combines highly efficient unit economics and consistent capital discipline with "
            "a highly resilient, conservative balance sheet. Its structural pricing power and defensive capital buffers "
            "position it in the top decile of its global sector peers, representing exceptional operational execution."
        )
    elif score >= 0.52:
        summary = (
            f"{ticker} maintains a solid, Tier {tier} quantamental profile (Score: {score:.3f}). "
            "Core operational metrics and capital discipline track within long-term sector averages. "
            "While the business is structurally sound with comfortable solvency safeguards, growth velocity and "
            "margin parameters remain sensitive to competitive industry pressures and cyclical changes."
        )
    elif score >= 0.35:
        summary = (
            f"{ticker} displays a bifurcated, Tier {tier} quality profile (Score: {score:.3f}). "
            "Although the company retains baseline liquidity cover, it is constrained by compressed margins, "
            "sluggish capital allocation efficiency, or elevated debt service obligations. Sustaining shareholder "
            "returns will depend on structural cost adjustments and defensive balance sheet management."
        )
    else:
        summary = (
            f"{ticker} operates under a distressed or highly speculative Tier {tier} quantamental profile (Score: {score:.3f}). "
            "The company is severely restricted by negative cash conversion, high debt leverage, or structural margin erosion. "
            "This defensive posture is highly sensitive to capital market conditions and requires significant capital restructuring."
        )

    return {
        "summary": summary,
        "unit_economics_score": ue_text,
        "capital_discipline_score": cd_text,
        "balance_sheet_score": bs_text,
        "hedge_book_score": h_text,
        "reserves_score": r_text,
        "operational_score": op_text,
        "sentiment_score": s_text,
        "macro_sensitivity_score": m_text
    }


# High-fidelity deterministic E&P fallback matrix
def get_ep_deterministic_fallback(data: dict) -> dict:
    """Highly descriptive, structural, and geology-themed deterministic fallback for Permian E&P tickers.
    
    Provides elite, institutional context (Delaware vs. Midland basins, horizontal well economics)
    even when the Gemini API is unavailable.
    """
    ticker = data.get("ticker", "ticker").upper()
    score = data.get("caligula_score", 0.5)
    tier = data.get("tier", "B")
    
    # Basin and geological mapping by ticker (Midland vs Delaware)
    delaware_operators = ["FANG", "EOG", "OVV", "APA", "CTRA", "CRGY", "CIVI"]
    midland_operators = ["MTDR", "SM", "VTLE", "PXD", "CPE", "CXO", "PR"]
    
    basin = "Delaware Basin" if ticker in delaware_operators else "Midland Basin"
    acreage_desc = (
        "deep, over-pressured Wolfcamp and Bone Spring formations" if basin == "Delaware Basin"
        else "high-margin Spraberry and Wolfcamp stacked pay zones"
    )

    # 1. Unit Economics
    ue_val = data.get("unit_economics_score", 0.5)
    if ue_val >= 0.70:
        ue_text = (
            f"Exhibits top-tier horizontal drilling economics in the {basin}, driven by low finding-and-development (F&D) "
            "costs per boe and high initial production (IP90) rates. High recycle ratios indicate elite operational cash flow generation."
        )
    else:
        ue_text = (
            f"Drilling efficiency in the {basin} is constrained by rising lease operating expenses (LOE) "
            "or higher localized water handling costs, slightly compressing the cash operating recycle ratio."
        )

    # 2. Capital Discipline
    cd_val = data.get("capital_discipline_score", 0.5)
    if cd_val >= 0.70:
        cd_text = (
            f"Demonstrates exemplary capital discipline with a robust reinvestment rate of under 50%, "
            "maximizing free cash flow yield. Well capital expenditure tracks below basin averages, supporting consistent dividend structures."
        )
    else:
        cd_text = (
            f"Capital yield is impacted by elevated well development cost inflation or higher infrastructure build-out "
            f"requirements across the {basin} acreage, reducing discretionary free cash generation."
        )

    # 3. Balance Sheet
    bs_val = data.get("balance_sheet_score", 0.5)
    if bs_val >= 0.70:
        bs_text = (
            "Maintains an elite, low-leverage balance sheet. The company operates with a Net Debt to EBITDAX ratio "
            "well within defensive limits, maintaining a fortress liquidity buffer to navigate oil price volatility."
        )
    else:
        bs_text = (
            "Leverage parameters are slightly elevated compared to top-tier Permian peers. Increased credit facility drawdown "
            "reduces balance sheet flexibility during sharp commodity downcycles."
        )

    # 4. Risk Mitigation & Hedging
    h_val = data.get("hedge_book_score", 0.5)
    if h_val >= 0.70:
        h_text = (
            "Maintains an actively managed, institutional hedge book. Comprehensive swap and collar positions secure "
            "cash flow stability, establishing highly defensive floors against sudden commodity market drawdowns."
        )
    else:
        h_text = (
            "Carries high exposure to unhedged spot prices. While this maximizes upside capture, it leaves cash flow "
            "highly sensitive to sudden WTI benchmark declines and widening regional basis differentials."
        )

    # 5. Growth & Asset Lifespan
    r_val = data.get("reserves_score", 0.5)
    if r_val >= 0.70:
        r_text = (
            f"Maintains a deep inventory of premium Tier-1 horizontal drilling locations across the {acreage_desc}. "
            "High proved developed (1P) reserve replacement ratios guarantee multi-decade acreage viability."
        )
    else:
        r_text = (
            f"Suffers from accelerating Tier-1 inventory depletion or rising development saturation on legacy {basin} blocks, "
            "shortening the primary low-cost acreage lifespan."
        )

    # 6. Operational Momentum
    op_val = data.get("operational_score", 0.5)
    if op_val >= 0.70:
        op_text = (
            f"Maintains strong operational momentum with robust daily BOE production growth and superior horizontal well "
            f"lateral lengths exceeding 10,000 feet. Advanced completions techniques maximize acreage recovery ratios."
        )
    else:
        op_text = (
            f"Operational momentum faces minor geological friction, marked by well-interference patterns or rising gas-to-oil "
            f"ratios (GOR) on mature horizontal pads in the {basin}."
        )

    # 7. Sentiment
    s_val = data.get("sentiment_score", 0.5)
    if s_val >= 0.70:
        s_text = (
            "Supported by exceptionally strong institutional ownership and insider alignment. Minimal short interest reflects "
            "high market confidence in the operator's acreage quality and cash return strategy."
        )
    else:
        s_text = (
            "Subject to moderate short interest pressure. Market skepticism focuses on inventory lifespans or regional takeaway "
            "pipeline bottlenecks, prompting elevated hedging activity from market makers."
        )

    # 8. Macro Sensitivity
    m_val = data.get("macro_sensitivity_score", 0.5)
    if m_val >= 0.70:
        m_text = (
            "Exhibits high commodity resilience, displaying a low downside beta relative to WTI index movements. "
            "The low cash breakeven profile secures profitable production margins even under a sub-$50 WTI stress scenario."
        )
    else:
        m_text = (
            "Highly sensitive to WTI oil price volatility. The elevated asset breakeven threshold increases cash flow "
            "drawdown risks during extended commodity downturns."
        )

    # Cohesive E&P Strategic Summary
    if score >= 0.70:
        summary = (
            f"{ticker} displays an exceptional, Tier {tier} E&P geological profile in the {basin} (Score: {score:.3f}). "
            f"Sustained by premium Tier-1 horizontal acreage in the {acreage_desc}, the operator combines world-class "
            "F&D costs and high recycle ratios with an elite, low-leverage balance sheet. Exceptional capital discipline "
            "positions the company as a premier defensive cash-generating asset in the Permian Basin."
        )
    elif score >= 0.52:
        summary = (
            f"{ticker} maintains a solid, highly productive Tier {tier} operational profile in the {basin} (Score: {score:.3f}). "
            f"While the company controls stable, profitable core acreage in the {acreage_desc}, its free cash yield remains "
            "moderately sensitive to WTI price fluctuations, infrastructure build-outs, and localized water-management expenditures."
        )
    else:
        summary = (
            f"{ticker} operates under a constrained, Tier {tier} geological profile (Score: {score:.3f}). "
            f"Sustaining returns on its {basin} acreage is challenged by rising finding costs, inventory depletion on "
            "legacy blocks, or high leverage. Strategic restructuring or consolidation represents the primary path to capital recovery."
        )

    return {
        "summary": summary,
        "unit_economics_score": ue_text,
        "capital_discipline_score": cd_text,
        "balance_sheet_score": bs_text,
        "hedge_book_score": h_text,
        "reserves_score": r_text,
        "operational_score": op_text,
        "sentiment_score": s_text,
        "macro_sensitivity_score": m_text
    }


# Serverless Gemini REST Client for Permian E&P study tickers
def get_ep_gemini_narratives(data: dict) -> dict:
    """Calls Google's Gemini 1.5 Flash API via REST to generate objective, high-fidelity geological insights.
    
    Utilizes direct REST API queries to bypass heavy SDK wrappers and minimize Vercel bundle sizes.
    Includes a robust local fallback if the API key is missing, invalid, or rate-limited.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("INFO: No GEMINI_API_KEY found. Gracefully falling back to deterministic E&P narrative matrix.")
        return get_ep_deterministic_fallback(data)
        
    ticker = data.get("ticker", "ticker").upper()
    score = data.get("caligula_score", 0.5)
    tier = data.get("tier", "B")
    
    # Compile a descriptive context packet of E&P scores to feed the prompt
    p_data = {
        "ticker": ticker,
        "caligula_score": f"{score:.3f}",
        "tier": tier,
        "unit_economics": f"{data.get('unit_economics_score', 0.5):.2f}",
        "capital_discipline": f"{data.get('capital_discipline_score', 0.5):.2f}",
        "balance_sheet": f"{data.get('balance_sheet_score', 0.5):.2f}",
        "risk_hedging": f"{data.get('hedge_book_score', 0.5):.2f}",
        "inventory_reserves": f"{data.get('reserves_score', 0.5):.2f}",
        "operational_momentum": f"{data.get('operational_score', 0.5):.2f}",
        "market_sentiment": f"{data.get('sentiment_score', 0.5):.2f}",
        "macro_sensitivity": f"{data.get('macro_sensitivity_score', 0.5):.2f}"
    }

    # Strict system-level prompt guiding academic tone, geology context, and strict compliance
    prompt = (
        "You are an elite, institutional quant E&P (Exploration & Production) energy research analyst. "
        "Your task is to translate raw quantitative quality scores into objective, context-aware operational narratives.\n\n"
        
        f"Input Data:\n{json.dumps(p_data, indent=2)}\n\n"
        
        "CRITICAL RULES:\n"
        "1. DO NOT give financial advice, buy/sell recommendations, or subjective opinions. Remain strictly factual and academic.\n"
        "2. Do not use generic filler text or hyperbole. Explain how these metrics reflect their geological acreage (Delaware Basin or Midland Basin), "
        "well finding-and-development (F&D) economics, recycle ratios, lateral lengths, inventory lifetimes, proved reserves (1P), leverage profiles, and breakeven floors.\n"
        "3. Keep all descriptions brief, dense, and institutional.\n"
        "4. You MUST output a valid JSON object matching the SCHEMA below. Do not include markdown code block formatting (like ```json). Return ONLY the raw JSON string.\n\n"
        
        "JSON SCHEMA:\n"
        "{\n"
        '  "summary": "1-2 sentence executive overview linking their overall E&P score, tier, basin location, and operational standing.",\n'
        '  "unit_economics_score": "Factual description of horizontal well F&D costs, recycle ratios, and margins.",\n'
        '  "capital_discipline_score": "Objective assessment of reinvestment rates, FCF yields, and capex budgets.",\n'
        '  "balance_sheet_score": "Factual leverage status (Debt/EBITDAX) and liquidity metrics.",\n'
        '  "hedge_book_score": "Objective hedging status (swaps/collars) and commodity price sensitivity.",\n'
        '  "reserves_score": "Assesses Tier-1 horizontal location inventory depth and 1P reserve replacement ratios.",\n'
        '  "operational_score": "Review of daily BOE production trajectories, well lateral lengths, and completions momentum.",\n'
        '  "sentiment_score": "Objective summary of market positioning, institutional backing, and short cover ratios.",\n'
        '  "macro_sensitivity_score": "Defines commodity price breakeven floors (WTI) and structural beta."\n'
        "}"
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    try:
        res = requests.post(url, headers=headers, json=body, timeout=8.0)
        if res.status_code == 200:
            res_data = res.json()
            raw_text = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            # Parse and clean the generated JSON
            parsed = json.loads(raw_text)
            
            # Verify all keys exist, otherwise patch from deterministic fallback
            fallback = get_ep_deterministic_fallback(data)
            required_keys = [
                "summary", "unit_economics_score", "capital_discipline_score", "balance_sheet_score",
                "hedge_book_score", "reserves_score", "operational_score", "sentiment_score", "macro_sensitivity_score"
            ]
            for key in required_keys:
                if key not in parsed or not parsed[key]:
                    parsed[key] = fallback[key]
                    
            return parsed
        else:
            print(f"WARN: Gemini API returned status {res.status_code}. Details: {res.text}")
            return get_ep_deterministic_fallback(data)
    except requests.exceptions.Timeout as e:
        print(f"WARN: Gemini API call timed out: {e}. Falling back to deterministic E&P matrix.")
        return get_ep_deterministic_fallback(data)
    except requests.exceptions.RequestException as e:
        print(f"WARN: Gemini API network request failed: {e}. Falling back to deterministic E&P matrix.")
        return get_ep_deterministic_fallback(data)
    except json.JSONDecodeError as e:
        print(f"WARN: Gemini API returned invalid JSON: {e}. Falling back to deterministic E&P matrix.")
        return get_ep_deterministic_fallback(data)
    except Exception as e:
        print(f"WARN: Gemini API general failure: {e}. Falling back to deterministic E&P matrix.")
        return get_ep_deterministic_fallback(data)
