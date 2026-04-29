from __future__ import annotations

import streamlit as st

from modules.m1_pow_monitor import render_m1
from modules.m2_block_header import render_m2
from modules.m3_difficulty_history import render_m3
from modules.m4_ai_anomaly import render_m4


st.set_page_config(
    page_title="CryptoChain Analyzer Dashboard",
    page_icon="C",
    layout="wide",
)

st.title("CryptoChain Analyzer Dashboard")
st.caption(
    "Bitcoin live metrics, proof-of-work verification, difficulty history, and AI-driven analysis."
)

with st.sidebar:
    st.header("Project Status")
    st.markdown("- M1: operational")
    st.markdown("- M2: operational")
    st.markdown("- M3: operational")
    st.markdown("- M4: checkpoint skeleton")
    st.info("Checkpoint 29 April: M1, M2, and M3 are visible in the dashboard.")

overview_tab, m1_tab, m2_tab, m3_tab, m4_tab = st.tabs(
    [
        "Overview",
        "M1 Proof of Work",
        "M2 Block Header",
        "M3 Difficulty History",
        "M4 AI",
    ]
)

with overview_tab:
    st.subheader("Roadmap")
    st.markdown(
        """
        1. Connect to live Bitcoin APIs.
        2. Build the Proof of Work monitor.
        3. Verify the latest block header locally.
        4. Plot difficulty adjustment history.
        5. Add the anomaly detector and evaluate it.
        """
    )
    st.success("Base project structure is ready.")

with m1_tab:
    render_m1()

with m2_tab:
    render_m2()

with m3_tab:
    render_m3()

with m4_tab:
    render_m4()
