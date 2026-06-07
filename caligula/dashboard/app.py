"""Streamlit dashboard consuming public JSON data."""

import streamlit as st
import json
import pandas as pd
from caligula.config import WEBSITE_DIR

st.set_page_config(page_title="Project Caligula", layout="wide")


def load_data():
    path = WEBSITE_DIR / "public_caligula_data.json"
    if not path.exists():
        st.error(
            "Canonical JSON data not found. Run the backtest and export pipeline first."
        )
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    st.title("Project Caligula: Institutional E&P Valuation")

    data = load_data()
    if not data:
        return

    st.write(f"**Data As Of:** {data.get('generated_at', 'Unknown')}")

    st.header("DCF Outputs")
    dcf_df = pd.DataFrame(data.get("dcf_summary", []))
    if not dcf_df.empty:
        st.dataframe(dcf_df)
    else:
        st.info("No DCF data available.")

    st.header("Performance Ledger")
    perf_df = pd.DataFrame(data.get("performance_ledger", []))
    if not perf_df.empty:
        st.dataframe(perf_df)
    else:
        st.info("No performance data available.")


if __name__ == "__main__":
    main()
