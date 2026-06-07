"""Streamlit dashboard consuming public JSON data."""

import json
import streamlit as st
import pandas as pd
from caligula.config import WEBSITE_DIR

st.set_page_config(page_title="Project Caligula", layout="wide")

_PCT_COLS = {"cagr", "volatility", "max_drawdown", "hit_rate",
             "wacc", "implied_upside"}


def load_data():
    path = WEBSITE_DIR / "public_caligula_data.json"
    if not path.exists():
        st.error("Pipeline data unavailable — generate outputs/website/public_caligula_data.json.")
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _fmt_pct(v):
    return f"{v * 100:.1f}%" if v is not None else "N/A"


def _fmt_float(v, decimals=2):
    return f"{v:.{decimals}f}" if v is not None else "N/A"


# ── Tab renderers ─────────────────────────────────────────────────────────────

def render_rankings(data):
    st.header("Quality Ledger")
    rankings = data.get("rankings", [])
    if not rankings:
        st.info("No active study rankings compiled.")
        return
    df = pd.DataFrame(rankings)
    display_cols = [c for c in [
        "rank", "ticker", "tier", "composite",
        "unit_econ", "capital_discipline", "balance_sheet",
        "hedge_book", "reserves", "operational", "sentiment", "macro",
    ] if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True, hide_index=True)


def render_quarterly_ledger(data):
    st.header("Quarterly Detail Ledger")
    rankings = data.get("rankings", [])
    if not rankings:
        st.info("No published rows available.")
        return
    df = pd.DataFrame(rankings)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_deep_dive(data):
    st.header("Single-Name Deep Dive")
    deep_dive = data.get("deep_dive", {})
    if not deep_dive:
        st.info("No published deep-dive data available.")
        return

    tickers = sorted(deep_dive.keys())
    selected = st.selectbox("Select ticker", tickers)
    if not selected:
        return

    entry = deep_dive[selected]
    composite = entry.get("composite")
    tier = entry.get("tier", "N/A")

    col1, col2, col3 = st.columns(3)
    col1.metric("Composite Score", _fmt_float(composite))
    col2.metric("Tier", tier)
    col3.metric("Company", entry.get("company", selected))

    st.caption(entry.get("narrative", ""))

    metrics = entry.get("metrics", [])
    if metrics:
        st.subheader("Pillar Scores")
        mdf = pd.DataFrame(metrics)
        st.dataframe(mdf, use_container_width=True, hide_index=True)

    history = entry.get("history", [])
    if history:
        st.subheader("Score History")
        hdf = pd.DataFrame(history).set_index("quarter")
        st.line_chart(hdf["score"])
    else:
        st.caption("No multi-quarter history available yet.")


def render_dcf(data):
    st.header("EOG DCF Overlay")
    dcf = data.get("dcf_summary", [])
    if not dcf:
        st.info("No published DCF rows available.")
        return

    eog_rows = [r for r in dcf if str(r.get("ticker", "")).upper() == "EOG"]
    if not eog_rows:
        st.info("EOG is not in the published DCF dataset.")
        return

    row = eog_rows[0]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("WACC", _fmt_pct(row.get("wacc")))
    col2.metric("Intrinsic (Reserve Life)", f"${row.get('intrinsic_price_reserve_life', 'N/A')}")
    col3.metric("Intrinsic (Exit Multiple)", f"${row.get('intrinsic_price_exit_multiple', 'N/A')}")
    col4.metric("Implied Upside", _fmt_pct(row.get("implied_upside")))

    st.caption(
        f"Recommendation: **{row.get('recommendation', 'N/A')}**  |  "
        f"Valuation Date: {row.get('valuation_date', 'N/A')}  |  "
        f"Terminal Value: ${row.get('terminal_value', 'N/A'):,.0f}M"
        if isinstance(row.get("terminal_value"), (int, float)) else
        f"Recommendation: **{row.get('recommendation', 'N/A')}**  |  Valuation Date: {row.get('valuation_date', 'N/A')}"
    )

    st.dataframe(pd.DataFrame([row]), use_container_width=True, hide_index=True)

    # Also surface EOG in deep_dive if available
    deep_dive = data.get("deep_dive", {})
    if "EOG" in deep_dive:
        eog = deep_dive["EOG"]
        st.subheader("EOG Caligula Quality Score")
        col1, col2 = st.columns(2)
        col1.metric("Composite Score", _fmt_float(eog.get("composite")))
        col2.metric("Tier", eog.get("tier", "N/A"))
        st.caption(eog.get("narrative", ""))


def render_performance(data):
    st.header("Performance Ledger")
    backtests = data.get("backtests", {})
    perf_ledger = data.get("performance_ledger", [])

    if not backtests and not perf_ledger:
        st.info("Pipeline data unavailable — generate outputs/website/public_caligula_data.json.")
        return

    ep = backtests.get("ep_study", {})
    stats = ep.get("stats", {})
    if stats:
        st.subheader("E&P Study — Summary Statistics")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("CAGR",         _fmt_pct(stats.get("cagr")))
        col2.metric("Volatility",   _fmt_pct(stats.get("volatility")))
        col3.metric("Sharpe",       _fmt_float(stats.get("sharpe")))
        col4.metric("Max Drawdown", _fmt_pct(stats.get("max_drawdown")))
        col5.metric("Hit Rate",     _fmt_pct(stats.get("hit_rate")))
    else:
        st.info("No summary statistics available.")

    wealth_path = ep.get("wealth_path", [])
    if wealth_path:
        st.subheader("Wealth Path")
        wpdf = pd.DataFrame(wealth_path).set_index("quarter")
        st.line_chart(wpdf[["strategy", "benchmark"]])
    else:
        st.caption("Wealth path series not yet compiled — per-quarter return data required.")

    quarterly_returns = ep.get("quarterly_returns", [])
    if quarterly_returns:
        st.subheader("Quarterly Returns")
        st.dataframe(pd.DataFrame(quarterly_returns), use_container_width=True, hide_index=True)
    else:
        st.caption("Quarterly return breakdown not yet compiled.")

    if perf_ledger:
        st.subheader("Full Performance Ledger")
        st.dataframe(pd.DataFrame(perf_ledger), use_container_width=True, hide_index=True)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    st.title("Project Caligula: Institutional E&P Valuation")

    data = load_data()
    if not data:
        return

    st.caption(f"Data as of: {data.get('generated_at', 'Unknown')}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Quality Ledger",
        "Quarterly Detail",
        "Deep Dive",
        "EOG DCF",
        "Performance Ledger",
    ])

    with tab1:
        render_rankings(data)
    with tab2:
        render_quarterly_ledger(data)
    with tab3:
        render_deep_dive(data)
    with tab4:
        render_dcf(data)
    with tab5:
        render_performance(data)


if __name__ == "__main__":
    main()
