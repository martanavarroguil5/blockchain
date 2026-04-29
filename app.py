from __future__ import annotations

import streamlit as st

from modules.m1_pow_monitor import render_m1
from modules.m2_block_header import render_m2
from modules.m3_difficulty_history import render_m3
from modules.m4_ai_anomaly import render_m4
from modules.ui import apply_app_theme, hero, insight_grid


st.set_page_config(
    page_title="CryptoChain Analyzer Dashboard",
    page_icon="C",
    layout="wide",
)

apply_app_theme()
hero()

with st.sidebar:
    st.header("Project Status")
    st.markdown("**Student:** Marta Navarro")
    st.markdown("**Project:** Bitcoin Proof Explorer")
    st.divider()
    st.markdown("- M1: operational")
    st.markdown("- M2: operational")
    st.markdown("- M3: operational")
    st.markdown("- M4: checkpoint skeleton")
    st.info("Checkpoint 29 April: core modules are visible and connected to live Bitcoin data.")

selected_page = st.radio(
    "Dashboard section",
    [
        "Overview",
        "M1 Proof of Work",
        "M2 Block Header",
        "M3 Difficulty History",
        "M4 AI",
    ],
    horizontal=True,
    label_visibility="collapsed",
)

if selected_page == "Overview":
    st.subheader("Checkpoint Overview")
    insight_grid(
        [
            ("Core status", "3 / 3", "M1, M2, and M3 are operational for the checkpoint."),
            ("Live source", "API fallback", "The dashboard uses Blockstream first and Mempool.space if a rate limit appears."),
            ("AI direction", "Anomaly detection", "M4 uses block interval outliers as the selected analytical approach."),
        ]
    )
    st.markdown("#### Delivery roadmap")
    st.dataframe(
        {
            "Module": ["M1", "M2", "M3", "M4"],
            "Checkpoint result": [
                "Live mining metrics and block interval charts",
                "Local double SHA-256 header verification",
                "Difficulty adjustment history and timing ratio",
                "Anomaly detector skeleton with live preview",
            ],
            "Status": ["Operational", "Operational", "Operational", "Skeleton"],
        },
        width="stretch",
        hide_index=True,
    )
    st.success("The project is aligned with the 29 April checkpoint requirements.")

elif selected_page == "M1 Proof of Work":
    render_m1()

elif selected_page == "M2 Block Header":
    render_m2()

elif selected_page == "M3 Difficulty History":
    render_m3()

elif selected_page == "M4 AI":
    render_m4()
