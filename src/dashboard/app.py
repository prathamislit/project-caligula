"""Streamlit dashboard — primary recruiter-facing deliverable for Project Caligula.

Completely overhauled to match the bespoke minimalist editorial design of investwithsnp.vercel.app.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Make src importable when running via `streamlit run`
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.utils.config import DATA_DIR, load_weights, load_universe
from src.backtest.portfolio_engine import build_portfolio, compute_returns, performance_stats

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CALIGULA · Research",
    layout="wide",
    page_icon="🏛️",
    initial_sidebar_state="expanded",
)

# Custom Design Palette
TIER_COLORS = {
    "A": "#B8922A",  # Gold
    "B": "#E0D8C3",  # Darker Sand
    "C": "#55504A",  # Ash
    "D": "#1C1C18",  # Slate Dark
}

PILLAR_LABELS = {
    "unit_economics": "Unit Economics",
    "capital_discipline": "Capital Discipline",
    "balance_sheet": "Balance Sheet Resilience",
    "hedge_book": "Hedge Book Quality",
    "reserves": "Reserves & Inventory",
    "operational": "Operational Momentum",
    "sentiment": "Sentiment Signals",
    "macro_sensitivity": "Macro Sensitivity",
}

# ── Bulletproof HTML Rendering Function ───────────────────────────────────────
def render_html(html_str):
    """Clean leading spaces of every line to prevent markdown code-block rendering."""
    cleaned = "\n".join([line.strip() for line in html_str.split("\n")])
    st.markdown(cleaned, unsafe_allow_html=True)

# ── Inject Custom CSS for Editorial Vercel Aesthetic ──────────────────────────
def inject_custom_css():
    render_html(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&display=swap" rel="stylesheet">
        
        <style>
        /* CSS variables matching investwithsnp.vercel.app */
        :root {
            --p: #EDE5D0;
            --pd: #E0D8C3;
            --bg: #faf9f5;
            --ink: #111008;
            --ash: #55504A;
            --gh: #7A766E;
            --acc: #3D3A33;
            --go: #B8922A;
            --sl: #1C1C18;
            --good: #2A6E2A;
            --serif: 'EB Garamond', Georgia, serif;
            --mono: 'Courier New', Courier, monospace;
        }

        /* Override general body background and text */
        .stApp {
            background-color: var(--bg) !important;
            color: var(--ink) !important;
            font-family: var(--serif) !important;
        }
        
        /* Font and text color for normal elements */
        div, p, label, span, li, a {
            font-family: var(--serif);
            color: var(--ink);
        }

        /* Headings styling */
        h1, h2, h3, h4, h5, h6 {
            font-family: var(--serif) !important;
            color: var(--ink) !important;
            font-weight: 500 !important;
            margin-bottom: 20px !important;
            margin-top: 10px !important;
        }
        
        h1 {
            font-size: clamp(32px, 5vw, 64px) !important;
            line-height: 1.1 !important;
            letter-spacing: -.015em !important;
        }
        
        h2 {
            font-size: 28px !important;
            line-height: 1.25 !important;
        }

        h3 {
            font-size: 22px !important;
            line-height: 1.3 !important;
        }
        
        em {
            font-style: italic !important;
            font-weight: 400 !important;
        }

        /* Style Streamlit Sidebar */
        [data-testid="stSidebar"] {
            background-color: var(--p) !important;
            border-right: 1px solid rgba(17,16,8,0.12) !important;
        }
        
        [data-testid="stSidebar"] * {
            font-family: var(--serif) !important;
            color: var(--ink) !important;
        }
        
        /* Sidebar Radio Buttons minimal design */
        [data-testid="stSidebar"] .stRadio > label {
            font-family: var(--mono) !important;
            font-size: 9px !important;
            letter-spacing: .2em !important;
            text-transform: uppercase !important;
            color: var(--ash) !important;
            margin-bottom: 12px !important;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] {
            gap: 6px !important;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] label {
            background-color: transparent !important;
            border: 1px solid rgba(17,16,8,0.1) !important;
            border-radius: 0px !important;
            padding: 10px 14px !important;
            font-family: var(--mono) !important;
            font-size: 11px !important;
            letter-spacing: .1em !important;
            text-transform: uppercase !important;
            cursor: pointer;
            transition: all 0.2s !important;
            margin-bottom: 4px !important;
            width: 100% !important;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background-color: var(--pd) !important;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
            background-color: var(--ink) !important;
            color: var(--p) !important;
            border-color: var(--ink) !important;
        }
        
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] * {
            color: var(--p) !important;
        }
        
        /* Hide default radio circle icon in sidebar */
        [data-testid="stSidebar"] div[role="radiogroup"] label span[data-testid="stWidgetLabel"]::before {
            display: none !important;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
            font-family: var(--mono) !important;
            font-size: 11px !important;
            letter-spacing: 0.05em !important;
        }

        /* Top Bar and MainMenu styling */
        header, [data-testid="stHeader"] {
            background-color: rgba(237,229,208,0.8) !important;
            backdrop-filter: blur(10px) !important;
            border-bottom: 1px solid rgba(17,16,8,0.1) !important;
        }
        
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important;}

        /* Custom cell-grid style layout */
        .cell-grid {
            display: grid;
            gap: 1px;
            background: rgba(17,16,8,0.1);
            width: 100%;
            margin-bottom: 24px;
        }
        .cell-grid.cols-3 { grid-template-columns: repeat(3, 1fr); }
        .cell-grid.cols-4 { grid-template-columns: repeat(4, 1fr); }
        .cell-grid.cols-5 { grid-template-columns: repeat(5, 1fr); }
        
        .cell {
            background: var(--p);
            padding: 24px 20px;
            transition: background 0.15s;
        }
        .cell:hover {
            background: var(--pd);
        }
        .cell-num {
            font-family: var(--mono);
            font-size: 8px;
            letter-spacing: .2em;
            color: var(--gh);
            margin-bottom: 10px;
        }
        .cell-code {
            font-family: var(--mono);
            font-size: 10px;
            letter-spacing: .12em;
            color: var(--ink);
            margin-bottom: 8px;
            font-weight: 700;
        }
        .cell-title {
            font-size: 18px;
            color: var(--ink);
            margin-bottom: 8px;
            line-height: 1.3;
            font-weight: 500;
        }
        .cell-body {
            font-size: 13.5px;
            line-height: 1.7;
            color: var(--ash);
        }
        .cell-tag {
            font-family: var(--mono);
            font-size: 8px;
            letter-spacing: .12em;
            color: var(--ink);
            margin-top: 10px;
            font-weight: 600;
        }

        /* Metric cards styled like Vercel site's impact stats */
        .stat-strip {
            display: grid;
            gap: 1px;
            background: rgba(17,16,8,0.08);
            margin-top: 16px;
            margin-bottom: 32px;
            width: 100%;
        }
        .stat-cell {
            background: var(--p);
            padding: 20px 16px;
            border-left: 2px solid var(--go);
        }
        .stat-num {
            font-family: var(--serif);
            font-size: 32px;
            color: var(--ink);
            line-height: 1;
            margin-bottom: 4px;
            font-weight: 600;
        }
        .stat-num em {
            font-style: italic;
            color: var(--go);
        }
        .stat-key {
            font-family: var(--mono);
            font-size: 8px;
            letter-spacing: .14em;
            text-transform: uppercase;
            color: var(--ash);
        }

        /* Editorial Custom Table style */
        .results-wrap {
            overflow-x: auto;
            width: 100%;
            margin-bottom: 24px;
        }
        table.editorial-table {
            width: 100%;
            border-collapse: collapse;
            font-family: var(--serif);
        }
        table.editorial-table th {
            font-family: var(--mono);
            font-size: 9px;
            letter-spacing: .18em;
            text-transform: uppercase;
            color: var(--ash);
            text-align: left;
            padding: 10px 16px 10px 8px;
            border-bottom: 1px solid rgba(17,16,8,0.15);
            font-weight: 400;
            white-space: nowrap;
        }
        table.editorial-table td {
            font-size: 15px;
            color: var(--ink);
            padding: 12px 16px 12px 8px;
            border-bottom: 1px solid rgba(17,16,8,0.07);
        }
        table.editorial-table tr:hover td {
            background: rgba(184,146,42,0.04);
        }
        .td-sub {
            font-family: var(--mono);
            font-size: 10px;
            color: var(--ash);
        }
        .td-good {
            color: var(--good);
            font-weight: 600;
        }
        .td-warn {
            color: var(--go);
            font-weight: 600;
        }
        .td-risk {
            color: var(--ink);
        }

        /* Section dividers matching Vercel */
        .sec-label {
            font-family: var(--mono);
            font-size: 9px;
            letter-spacing: .24em;
            text-transform: uppercase;
            color: var(--ash);
            margin-bottom: 32px;
            margin-top: 32px;
            display: flex;
            align-items: center;
            gap: 14px;
            width: 100%;
        }
        .sec-label::after {
            content: '';
            flex: 1;
            height: 1px;
            background: rgba(17,16,8,.1);
        }

        /* Custom kicker styled text */
        .kicker {
            font-family: var(--mono);
            font-size: 9px;
            letter-spacing: .24em;
            text-transform: uppercase;
            color: var(--ash);
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 14px;
            width: 100%;
        }
        .kicker::before {
            content: '';
            width: 32px;
            height: 1px;
            background: var(--ash);
            flex: none;
        }

        /* Button styling matching the site */
        .stButton > button {
            height: 40px !important;
            padding: 0 24px !important;
            font-family: var(--mono) !important;
            font-size: 9px !important;
            letter-spacing: .18em !important;
            text-transform: uppercase !important;
            cursor: pointer !important;
            border-radius: 0px !important;
            font-weight: 500 !important;
            border: 1px solid rgba(17,16,8,.22) !important;
            background-color: transparent !important;
            color: var(--ink) !important;
            transition: all .2s !important;
        }
        
        .stButton > button:hover {
            border-color: var(--ink) !important;
            background-color: var(--ink) !important;
            color: var(--p) !important;
        }
        
        /* Selectbox and other inputs customization */
        div[data-baseweb="select"] > div {
            border-radius: 0px !important;
            border: 1px solid rgba(17,16,8,0.2) !important;
            background-color: var(--bg) !important;
            font-family: var(--mono) !important;
            font-size: 13px !important;
        }

        /* Info, Success, Warning alerts styling */
        div[data-testid="stAlert"] {
            border-radius: 0px !important;
            background-color: var(--p) !important;
            border: none !important;
            border-left: 4px solid var(--go) !important;
            color: var(--ink) !important;
        }
        div[data-testid="stAlert"] * {
            color: var(--ink) !important;
            font-family: var(--serif) !important;
        }

        /* Expanders custom styling */
        div[data-testid="stExpander"] {
            border-radius: 0px !important;
            border: 1px solid rgba(17,16,8,0.1) !important;
            background-color: var(--p) !important;
            margin-bottom: 8px !important;
        }
        div[data-testid="stExpander"] * {
            font-family: var(--serif) !important;
        }
        </style>
        """
    )

inject_custom_css()

# Helper to render custom stat strips
def render_custom_stat_strip(metrics_list):
    cols_count = len(metrics_list)
    cells = ""
    for m in metrics_list:
        cells += f"""
        <div class="stat-cell">
            <div class="stat-num">{m['val']}</div>
            <div class="stat-key">{m['key']}</div>
        </div>
        """
    render_html(
        f"""
        <div class="stat-strip" style="grid-template-columns: repeat({cols_count}, 1fr);">
            {cells}
        </div>
        """
    )

# Helper to apply clean Plotly formatting
def apply_plotly_theme(fig):
    fig.update_layout(
        font_family="EB Garamond, Georgia, serif",
        font_color="#111008",
        title_font_size=18,
        title_font_family="EB Garamond, Georgia, serif",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            gridcolor="rgba(17,16,8,0.06)",
            linecolor="rgba(17,16,8,0.15)",
            tickfont=dict(family="Courier New, monospace", size=10),
        ),
        yaxis=dict(
            gridcolor="rgba(17,16,8,0.06)",
            linecolor="rgba(17,16,8,0.15)",
            tickfont=dict(family="Courier New, monospace", size=10),
        ),
    )
    return fig

# ── Sidebar Wordmark & Nav ─────────────────────────────────────────────────────
render_html(
    """
    <div style="font-family: 'Courier New', monospace; font-size: 11px; letter-spacing: .26em; text-transform: uppercase; color: #111008; margin-bottom: 24px; margin-top: 10px;">
        CALIGULA &nbsp;·&nbsp; RESEARCH
    </div>
    """
)

view = st.sidebar.radio(
    "Navigation",
    ["Current Rankings", "Single-Name Deep Dive", "Backtest Results", "Methodology"],
    index=0,
)

# ── Load data ──────────────────────────────────────────────────────────────────
scores_path = DATA_DIR / "scores" / "all_scores.parquet"

@st.cache_data(ttl=3600)
def load_scores():
    if not scores_path.exists():
        return None
    df = pd.read_parquet(scores_path)
    df["quarter"] = pd.to_datetime(df["quarter"])
    return df

scores_df = load_scores()

# ── DEMO DATA (fallback) ──────────────────────────────────────────────────────
def make_demo_scores():
    rng = np.random.default_rng(42)
    uni = load_universe()["permian_universe"]
    tickers = [c["ticker"] for c in uni]
    quarters = pd.date_range("2020-01-01", "2025-12-31", freq="QE")
    rows = []
    base = {t: rng.uniform(0.35, 0.82) for t in tickers}
    for q in quarters:
        for t in tickers:
            score = float(np.clip(base[t] + rng.normal(0, 0.04), 0, 1))
            row = {"ticker": t, "quarter": q, "caligula_score": score}
            for p in PILLAR_LABELS:
                row[f"{p}_score"] = float(np.clip(
                    base[t] + rng.normal(0, 0.08), 0, 1
                ))
            tier = "A" if score >= 0.70 else "B" if score >= 0.52 else "C" if score >= 0.35 else "D"
            row["tier"] = tier
            rows.append(row)
    return pd.DataFrame(rows)

if scores_df is None:
    st.sidebar.warning("No backtest data found — showing demo scores.")
    scores_df = make_demo_scores()
    demo_mode = True
else:
    demo_mode = False

latest_quarter = scores_df["quarter"].max()
latest = scores_df[scores_df["quarter"] == latest_quarter].copy()

# ══════════════════════════════════════════════════════════════════════════════
# VIEW 1: Current Rankings
# ══════════════════════════════════════════════════════════════════════════════
if view == "Current Rankings":
    render_html(
        """
        <div class="kicker">Permian Basin E&P Diligence · MMXXVI</div>
        <h1>Structuring what<br>the spreadsheets<br><em>leave out.</em></h1>
        <p style="font-size: 19px; line-height: 1.85; color: #55504A; max-width: 680px; margin-bottom: 36px;">
            Our 8-pillar scoring engine targets under-followed Permian operators, converting unstructured disclosures 
            into a sector-normalized, point-in-time quality signal. Reserve levels, hedging profiles, and unit margins are resolved directly from footnotes.
        </p>
        """
    )
    
    if demo_mode:
        st.info("Demo mode: synthetic scores. Run `python run_backtest.py` to populate real historical data.")

    # Stat strip for Tiers
    tier_counts = latest["tier"].value_counts()
    metrics = [
        {"val": str(tier_counts.get("A", 0)), "key": "Tier A · Pristine"},
        {"val": str(tier_counts.get("B", 0)), "key": "Tier B · Quality"},
        {"val": str(tier_counts.get("C", 0)), "key": "Tier C · Median"},
        {"val": str(tier_counts.get("D", 0)), "key": "Tier D · Avoid"},
    ]
    render_custom_stat_strip(metrics)

    render_html('<div class="sec-label">Rankings Ledger</div>')

    # Rankings table prep
    display_cols = ["ticker", "tier", "caligula_score"] + [
        f"{p}_score" for p in PILLAR_LABELS if f"{p}_score" in latest.columns
    ]
    display_df = latest[[c for c in display_cols if c in latest.columns]].copy()
    display_df = display_df.sort_values("caligula_score", ascending=False).reset_index(drop=True)
    display_df.index += 1

    # Custom HTML editorial table rendering
    def render_rankings_table(df):
        score_cols = [c for c in df.columns if c.endswith("_score")]
        headers = ["Rank", "Ticker", "Tier", "Composite Score"] + [PILLAR_LABELS.get(c.replace("_score", ""), c) for c in score_cols]
        
        html = """
        <div class="results-wrap">
            <table class="editorial-table">
                <thead>
                    <tr>
        """
        for h in headers:
            html += f"<th>{h}</th>"
        html += """
                    </tr>
                </thead>
                <tbody>
        """
        for idx, row in df.iterrows():
            tier_class = "td-good" if row['tier'] == 'A' else "td-warn" if row['tier'] == 'B' else "td-risk" if row['tier'] == 'C' else ""
            html += f"""
                    <tr>
                        <td class="td-sub">{idx}</td>
                        <td style="font-weight: 600;">{row['ticker']}</td>
                        <td class="{tier_class}">{row['tier']}</td>
                        <td style="font-family: var(--mono); font-weight: bold; color: var(--go);">{row['caligula_score']:.3f}</td>
            """
            for sc in score_cols:
                val = row[sc]
                val_str = f"{val:.2f}" if pd.notna(val) else "N/A"
                val_class = "td-good" if val >= 0.70 else "td-warn" if val >= 0.50 else "td-risk"
                html += f'<td class="{val_class}" style="font-family: var(--mono);">{val_str}</td>'
            html += "</tr>"
        html += """
                </tbody>
            </table>
        </div>
        """
        render_html(html)

    render_rankings_table(display_df)

    # Composite score bar chart
    fig = px.bar(
        display_df.reset_index().rename(columns={"index": "rank"}),
        x="ticker",
        y="caligula_score",
        color="tier",
        color_discrete_map=TIER_COLORS,
        title=f"Caligula Composite Score Distribution — {latest_quarter.strftime('%Y Q%q') if hasattr(latest_quarter, 'quarter') else str(latest_quarter)[:7]}",
        labels={"caligula_score": "Score (0–1)", "ticker": ""},
        text="caligula_score",
    )
    fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig.update_layout(yaxis_range=[0, 1.15], showlegend=True)
    fig = apply_plotly_theme(fig)
    st.plotly_chart(fig, width="stretch")

    # Pillar heatmap
    render_html('<div class="sec-label">Pillar Score Heatmap</div>')
    heat_cols = [f"{p}_score" for p in PILLAR_LABELS if f"{p}_score" in latest.columns]
    if heat_cols:
        sort_col = "caligula_score" if "caligula_score" in latest.columns else heat_cols[0]
        heat_df = latest.sort_values(sort_col, ascending=False).set_index("ticker")[heat_cols]
        heat_df.columns = [PILLAR_LABELS.get(c.replace("_score", ""), c) for c in heat_df.columns]
        
        custom_scale = [
            [0.0, "#1C1C18"],    # Dark Slate (Worst)
            [0.3, "#55504A"],    # Muted Ash
            [0.5, "#EDE5D0"],    # Cream Sand (Median)
            [0.8, "#E0D8C3"],    # Darker Sand
            [1.0, "#B8922A"],    # Beautiful Gold (Best)
        ]
        
        fig_heat = px.imshow(
            heat_df,
            color_continuous_scale=custom_scale,
            zmin=0, zmax=1,
            title="Pillar Scores by Operator",
            aspect="auto",
        )
        fig_heat.update_xaxes(tickangle=30)
        fig_heat = apply_plotly_theme(fig_heat)
        st.plotly_chart(fig_heat, width="stretch")

# ══════════════════════════════════════════════════════════════════════════════
# VIEW 2: Single-Name Deep Dive
# ══════════════════════════════════════════════════════════════════════════════
elif view == "Single-Name Deep Dive":
    tickers_available = sorted(scores_df["ticker"].unique())
    selected = st.sidebar.selectbox("Select Ticker", tickers_available)
    company_history = scores_df[scores_df["ticker"] == selected].sort_values("quarter")

    render_html(
        f"""
        <div class="kicker">Single-Name Deep Dive</div>
        <h1>Operator <em>{selected}</em> Analysis</h1>
        <p style="font-size: 18px; line-height: 1.8; color: #55504A; max-width: 680px; margin-bottom: 24px;">
            Tracking long-term operational trends, balance sheet leverage, and geological inventory replacement 
            for {selected} in the Permian Basin.
        </p>
        """
    )

    if not company_history.empty:
        latest_row = company_history.iloc[-1]
        score = latest_row.get("caligula_score", np.nan)
        tier = latest_row.get("tier", "—")
        date_str = str(latest_row["quarter"])[:10]
        
        # Calculate rank
        peer_df = latest.sort_values("caligula_score", ascending=False).reset_index(drop=True)
        peer_df.index += 1
        rank = peer_df[peer_df["ticker"] == selected].index[0] if selected in peer_df["ticker"].values else "—"

        metrics = [
            {"val": f"{score:.3f}" if pd.notna(score) else "N/A", "key": "Composite Score (0-1)"},
            {"val": f"Tier {tier}", "key": "Diligence Rating"},
            {"val": date_str, "key": "Reporting Date"},
            {"val": f"#{rank} / {len(peer_df)}", "key": "Universe Rank"},
        ]
        render_custom_stat_strip(metrics)

    # Score history line chart
    if "caligula_score" in company_history.columns:
        fig_hist = px.line(
            company_history,
            x="quarter",
            y="caligula_score",
            title=f"{selected} — Historical Caligula Score Path",
            labels={"caligula_score": "Score", "quarter": "Quarter"},
            markers=True,
        )
        fig_hist.update_traces(line_color="#B8922A", marker=dict(color="#111008", size=8))
        fig_hist.update_layout(yaxis_range=[0, 1.05])
        fig_hist = apply_plotly_theme(fig_hist)
        st.plotly_chart(fig_hist, width="stretch")

    # Pillar radar chart
    pillar_cols = [f"{p}_score" for p in PILLAR_LABELS if f"{p}_score" in company_history.columns]
    if pillar_cols and not company_history.empty:
        latest_pillars = company_history.iloc[-1][pillar_cols].dropna()
        labels = [PILLAR_LABELS.get(c.replace("_score", ""), c) for c in latest_pillars.index]
        values = latest_pillars.values.tolist()
        values_closed = values + [values[0]]
        labels_closed = labels + [labels[0]]

        fig_radar = go.Figure(go.Scatterpolar(
            r=values_closed,
            theta=labels_closed,
            fill="toself",
            name=selected,
            fillcolor="rgba(184, 146, 42, 0.15)",
            line_color="#B8922A",
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    gridcolor="rgba(17,16,8,0.08)",
                    linecolor="rgba(17,16,8,0.1)",
                    tickfont=dict(family="Courier New, monospace", size=9),
                ),
                angularaxis=dict(
                    gridcolor="rgba(17,16,8,0.08)",
                    tickfont=dict(family="EB Garamond, Georgia, serif", size=12),
                )
            ),
            title=f"{selected} — Pillar Coverage Breakdown",
        )
        fig_radar = apply_plotly_theme(fig_radar)
        st.plotly_chart(fig_radar, width="stretch")

    # Peer comparison
    render_html('<div class="sec-label">Sector Peer Comparison</div>')
    peer_df = latest[["ticker", "caligula_score", "tier"]].sort_values(
        "caligula_score", ascending=False
    ).reset_index(drop=True)
    peer_df.index += 1
    peer_df["highlight"] = peer_df["ticker"] == selected

    fig_peer = px.bar(
        peer_df,
        x="ticker",
        y="caligula_score",
        color="highlight",
        color_discrete_map={True: "#B8922A", False: "#EDE5D0"},
        title="Sector Rankings (Selected Highlighted in Gold)",
        labels={"caligula_score": "Score", "ticker": ""},
    )
    fig_peer.update_layout(showlegend=False, yaxis_range=[0, 1.05])
    fig_peer = apply_plotly_theme(fig_peer)
    st.plotly_chart(fig_peer, width="stretch")

# ══════════════════════════════════════════════════════════════════════════════
# VIEW 3: Backtest Results
# ══════════════════════════════════════════════════════════════════════════════
elif view == "Backtest Results":
    render_html(
        """
        <div class="kicker">Backtest Engine · 2014 Q1 to 2025 Q4</div>
        <h1>Historical <em>Variance</em> & Returns</h1>
        <p style="font-size: 18px; line-height: 1.8; color: #55504A; max-width: 680px; margin-bottom: 24px;">
            A 12-year point-in-time simulation rebalancing quarterly. We buy the top 25% highest-ranked E&P names (Long) 
            and short the bottom 25% (Short) to verify the risk-adjusted predictive power of our 8-pillar engine.
        </p>
        """
    )
    
    if demo_mode:
        st.info("Showing simulated backtest on demo scores. Real results require populated Parquet data.")

    portfolios = build_portfolio(scores_df, top_pct=0.25, bottom_pct=0.25)
    if not portfolios:
        st.warning("Insufficient quarterly data for backtest. Need at least 2 scored quarters.")
        st.stop()

    returns_df = compute_returns(portfolios)
    if returns_df.empty:
        st.warning("Could not compute returns — price data not yet downloaded.")
        st.stop()

    stats = performance_stats(returns_df)

    # Render metrics in Vercel Stat Strip
    metrics = [
        {"val": f"{stats.get('ann_return', 0):.1%}", "key": "Ann. L/S Return"},
        {"val": f"{stats.get('ann_vol', 0):.1%}", "key": "Ann. Volatility"},
        {"val": f"{stats.get('sharpe', 0):.2f}" if stats.get("sharpe") else "N/A", "key": "Sharpe Ratio"},
        {"val": f"{stats.get('max_drawdown', 0):.1%}", "key": "Max Drawdown"},
        {"val": f"{stats.get('hit_rate', 0):.1%}", "key": "Quarterly Hit Rate"},
    ]
    render_custom_stat_strip(metrics)

    # Cumulative return wealth path
    returns_df["cum_ls"] = (1 + returns_df["ls_return"]).cumprod()
    returns_df["cum_long"] = (1 + returns_df["long_return"]).cumprod()
    returns_df["cum_short"] = (1 + returns_df["short_return"]).cumprod()

    fig_cum = go.Figure()
    fig_cum.add_trace(go.Scatter(
        x=returns_df["quarter"], y=returns_df["cum_ls"],
        name="Long-Short (L/S)", line=dict(color="#B8922A", width=3)
    ))
    fig_cum.add_trace(go.Scatter(
        x=returns_df["quarter"], y=returns_df["cum_long"],
        name="Long Only", line=dict(color="#111008", width=1.5, dash="dot")
    ))
    fig_cum.add_trace(go.Scatter(
        x=returns_df["quarter"], y=returns_df["cum_short"],
        name="Short Only", line=dict(color="#55504A", width=1.5, dash="dot")
    ))
    fig_cum.update_layout(
        title="Cumulative Wealth Path (1.0 = Par)",
        yaxis_title="Wealth Factor",
        xaxis_title="Quarter",
    )
    fig_cum = apply_plotly_theme(fig_cum)
    st.plotly_chart(fig_cum, width="stretch")

    # Quarterly return bars
    fig_bar = px.bar(
        returns_df,
        x="quarter",
        y="ls_return",
        color=returns_df["ls_return"] > 0,
        color_discrete_map={True: "#B8922A", False: "#111008"},
        title="Quarterly L/S Returns Breakdown",
        labels={"ls_return": "L/S Return", "quarter": "Quarter"},
    )
    fig_bar.update_layout(showlegend=False)
    fig_bar = apply_plotly_theme(fig_bar)
    st.plotly_chart(fig_bar, width="stretch")

    # Custom editorial ledger table
    render_html('<div class="sec-label">Quarterly Detail Ledger</div>')

    html_ledger = """
    <div class="results-wrap">
        <table class="editorial-table">
            <thead>
                <tr>
                    <th>Quarter</th>
                    <th>Long Return</th>
                    <th>Short Return</th>
                    <th>L/S Net Return</th>
                    <th>N (Long)</th>
                    <th>N (Short)</th>
                </tr>
            </thead>
            <tbody>
    """
    for idx, row in returns_df.sort_values("quarter", ascending=False).iterrows():
        date_label = str(row['quarter'])[:7]
        long_ret = f"{row['long_return']:.2%}"
        short_ret = f"{row['short_return']:.2%}"
        ls_ret = f"{row['ls_return']:.2%}"
        
        ls_class = "td-good" if row['ls_return'] > 0 else "td-risk" if row['ls_return'] < 0 else ""
        
        html_ledger += f"""
                <tr>
                    <td class="td-sub" style="font-weight: 600;">{date_label}</td>
                    <td>{long_ret}</td>
                    <td>{short_ret}</td>
                    <td class="{ls_class}" style="font-family: var(--mono); font-weight: bold;">{ls_ret}</td>
                    <td class="td-sub">{int(row['n_long'])}</td>
                    <td class="td-sub">{int(row['n_short'])}</td>
                </tr>
        """
    html_ledger += """
            </tbody>
        </table>
    </div>
    """
    render_html(html_ledger)

# ══════════════════════════════════════════════════════════════════════════════
# VIEW 4: Methodology
# ══════════════════════════════════════════════════════════════════════════════
elif view == "Methodology":
    render_html(
        """
        <div class="kicker">Framework Methodology</div>
        <h1>Quantamental <em>Architecture</em></h1>
        <p style="font-size: 18px; line-height: 1.8; color: #55504A; max-width: 680px; margin-bottom: 32px;">
            A robust quantitative model needs rigorous definitions. Here is how we build, normalise, 
            and aggregate our 8-pillar corporate quality signal.
        </p>
        """
    )

    render_html('<div class="sec-label">The 8 Diligence Pillars</div>')

    # Custom 8-pillar cell-grid matching CHC Vercel platform cards
    pillar_cells_html = """
    <div class="cell-grid cols-4">
        <div class="cell">
            <div class="cell-code">UE — 18% Weight</div>
            <div class="cell-title">Unit <em>Economics</em></div>
            <div class="cell-body">
                Physical drilling profitability per barrel of oil. Tracks <strong>Finding & Development (F&D) Cost</strong> 
                and the <strong>Recycle Ratio</strong>. Higher means a superior asset base.
            </div>
            <div class="cell-tag">Direction: ↑ High</div>
        </div>
        <div class="cell">
            <div class="cell-code">CD — 15% Weight</div>
            <div class="cell-title">Capital <em>Discipline</em></div>
            <div class="cell-body">
                Efficiency of executive capital allocation. Tracks <strong>Free Cash Flow (FCF) Yield</strong> 
                and <strong>Capital Return Yield</strong> (buybacks & dividends).
            </div>
            <div class="cell-tag">Direction: ↑ High</div>
        </div>
        <div class="cell">
            <div class="cell-code">BS — 14% Weight</div>
            <div class="cell-title">Balance <em>Sheet</em></div>
            <div class="cell-body">
                Leverage safety buffers to survive downturns. Tracks <strong>Net Debt to EBITDAX</strong> 
                and <strong>Liquidity</strong> (cash + credit availability).
            </div>
            <div class="cell-tag">Direction: ↓ Low Debt</div>
        </div>
        <div class="cell">
            <div class="cell-code">HB — 12% Weight</div>
            <div class="cell-title">Hedge <em>Book</em></div>
            <div class="cell-body">
                Price protection insurance contracts parsed from footnotes. Scores the <strong>% of Production Hedged</strong> 
                and the <strong>Weighted Floor Price</strong> vs. strip.
            </div>
            <div class="cell-tag">Direction: ↑ High</div>
        </div>
        <div class="cell">
            <div class="cell-code">RE — 12% Weight</div>
            <div class="cell-title">Reserves & <em>Inventory</em></div>
            <div class="cell-body">
                Physical asset lifespan and exploration replacement. Tracks <strong>Tier-1 Inventory Years</strong> 
                and <strong>Organic Reserve Replacement</strong>.
            </div>
            <div class="cell-tag">Direction: ↑ High</div>
        </div>
        <div class="cell">
            <div class="cell-code">OM — 10% Weight</div>
            <div class="cell-title">Operational <em>Momentum</em></div>
            <div class="cell-body">
                Geological engineering efficiency gains in the field. Tracks <strong>Production growth per share</strong> 
                and the <strong>90-day Well Productivity Index</strong>.
            </div>
            <div class="cell-tag">Direction: ↑ High</div>
        </div>
        <div class="cell">
            <div class="cell-code">SS — 10% Weight</div>
            <div class="cell-title">Sentiment <em>Signals</em></div>
            <div class="cell-body">
                Insiders and short sellers behavior. Tracks <strong>Insider Net Buying</strong> (CEO/CFO purchases) 
                and the <strong>Short Interest Ratio</strong>.
            </div>
            <div class="cell-tag">Direction: ↑ Insiders / ↓ Shorts</div>
        </div>
        <div class="cell">
            <div class="cell-code">MS — 9% Weight</div>
            <div class="cell-title">Macro <em>Sensitivity</em></div>
            <div class="cell-body">
                Resilience to commodity shocks. Calculates the <strong>Downside WTI Beta</strong> 
                and the <strong>Drawdown Recovery Half-life</strong> after >20% sell-offs.
            </div>
            <div class="cell-tag">Direction: ↓ Low Beta</div>
        </div>
    </div>
    """
    render_html(pillar_cells_html)

    render_html('<div class="sec-label">Model Properties & Universe</div>')

    render_html(
        """
        <div class="cell-grid cols-3" style="margin-top: 24px;">
            <div class="cell">
                <div class="cell-code">UNIVERSE</div>
                <div class="cell-title">Point-in-Time <em>Operators</em></div>
                <div class="cell-body">
                    Consists of 13 Permian-weighted E&P operators (≥40% Permian production exposure). 
                    Includes historical merged/acquired operators (e.g. VTLE, CIVI, CPE, CXO) during their active periods 
                    to maintain absolute point-in-time validity and prevent survivorship bias.
                </div>
            </div>
            <div class="cell">
                <div class="cell-code">AGGREGATION</div>
                <div class="cell-title">Cross-Sectional <em>Percentiles</em></div>
                <div class="cell-body">
                    Each raw metric is cross-sectionally ranked (0.0 to 1.0) within the active sector universe at each quarter-end. 
                    Values are Winsorized at the 5th and 95th percentiles to clip extreme outliers before scoring.
                </div>
            </div>
            <div class="cell">
                <div class="cell-code">MISSING DATA</div>
                <div class="cell-title">Coverage <em>Adjustment</em></div>
                <div class="cell-body">
                    If a specific metric is unavailable for an operator in a quarter, the scoring engine dynamically 
                    reallocates its weight proportionally to the remaining active metrics within that specific pillar. 
                    This prevents empty denominators from skewing composite grades.
                </div>
            </div>
        </div>
        """
    )

    render_html('<div class="sec-label">Ingestion Architecture</div>')

    # Ingestion sources custom editorial table
    render_html(
        """
        <div class="results-wrap">
            <table class="editorial-table">
                <thead>
                    <tr>
                        <th>Source</th>
                        <th>Data Layer</th>
                        <th>Frequency</th>
                        <th>Purpose</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="font-weight: 600;">SEC EDGAR XBRL</td>
                        <td class="td-sub">Financial statements (10-K/Q)</td>
                        <td>Quarterly</td>
                        <td>Presents base balance sheet and income statement metrics (EBITDAX, Debt, cash-flow inputs)</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 600;">SEC Filing Footnotes</td>
                        <td class="td-sub">Unstructured tables & text</td>
                        <td>Quarterly</td>
                        <td>Processed by Google Gemini to extract exact hedge schedules, physical reserve replaced levels, and drilling unit costs</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 600;">yfinance API</td>
                        <td class="td-sub">Daily equity prices & metadata</td>
                        <td>Daily</td>
                        <td>Enables WTI beta computation, market caps, return statistics, and backtest portfolio wealth accumulation tracking</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 600;">FRED API</td>
                        <td class="td-sub">Macro rates & spot prices</td>
                        <td>Daily</td>
                        <td>Pulls WTI spot price series and interest rate spreads to frame historical macro conditions</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 600;">EIA DPR Portal</td>
                        <td class="td-sub">Rig counts & basin volumes</td>
                        <td>Monthly</td>
                        <td>Supplies physical production momentum indices for the Permian Basin</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 600;">FINRA API</td>
                        <td class="td-sub">Daily short sale volume</td>
                        <td>Daily</td>
                        <td>Feeds short interest sentiment indicators</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """
    )

# ── Shared Editorial Footer ───────────────────────────────────────────────────
render_html(
    """
    <div style="border-top: 1px solid rgba(17,16,8,0.08); margin-top: 64px; padding: 24px 0px 32px; display: flex; justify-content: space-between; align-items: center; gap: 20px; flex-wrap: wrap;">
        <span style="font-family: var(--mono); font-size: 9px; letter-spacing: .22em; text-transform: uppercase; color: var(--gh);">
            CALIGULA &nbsp;·&nbsp; QUANTAMENTAL RESEARCH &nbsp;·&nbsp; PENN STATE UNIVERSITY
        </span>
        <span style="font-family: var(--mono); font-size: 8px; letter-spacing: .1em; color: var(--gh); max-width: 580px; text-align: right; line-height: 1.7;">
            Academic research framework &nbsp;·&nbsp; Not investment advice &nbsp;·&nbsp; Not a solicitation &nbsp;·&nbsp; 
            Calculated indices are informational research outputs and do not constitute advisory services under SEC Rule 202(a)(11).
        </span>
    </div>
    """
)

st.sidebar.divider()
st.sidebar.caption("Project Caligula v2.0 | Pratham Shah")
if demo_mode:
    st.sidebar.caption("⚠️ Demo mode active")
