from __future__ import annotations

import streamlit as st


def render_m2() -> None:
    st.subheader("M2 - Block Header Analyzer")
    st.write(
        "This module will parse the latest 80-byte header, compute double SHA-256, and verify the proof of work locally."
    )
    st.warning("Pending implementation: fetch the latest block header and display its six fields.")
