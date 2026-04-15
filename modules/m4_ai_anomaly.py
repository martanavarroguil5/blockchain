from __future__ import annotations

import streamlit as st


def render_m4() -> None:
    st.subheader("M4 - AI Anomaly Detector")
    st.write(
        "Recommended approach: detect statistically unusual block inter-arrival times using live and historical Bitcoin data."
    )
    st.info(
        "Planned direction: start with a strong baseline using z-scores or Isolation Forest, then evaluate precision on labeled anomalies."
    )
