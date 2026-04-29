from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from api.blockchain_client import BlockchainApiError, get_client
from modules.ui import module_header, style_chart


@st.cache_data(ttl=300, show_spinner=False)
def load_anomaly_preview(block_limit: int = 120) -> pd.DataFrame:
    client = get_client()
    recent_blocks = client.get_recent_blocks_window(limit=block_limit)
    blocks_df = pd.DataFrame(recent_blocks).sort_values("height").reset_index(drop=True)
    blocks_df["timestamp_dt"] = pd.to_datetime(blocks_df["timestamp"], unit="s", utc=True)
    blocks_df["minutes_since_prev"] = blocks_df["timestamp"].diff() / 60
    blocks_df = blocks_df.dropna(subset=["minutes_since_prev"]).copy()

    mean_interval = blocks_df["minutes_since_prev"].mean()
    std_interval = blocks_df["minutes_since_prev"].std(ddof=1)
    if std_interval == 0 or not np.isfinite(std_interval):
        blocks_df["z_score"] = 0.0
    else:
        blocks_df["z_score"] = (blocks_df["minutes_since_prev"] - mean_interval) / std_interval
    blocks_df["is_candidate_anomaly"] = blocks_df["z_score"].abs() >= 2.5
    return blocks_df


def render_m4() -> None:
    module_header(
        "Module 4",
        "AI Anomaly Detector",
        "Checkpoint skeleton with the selected model direction, live block interval features, and a z-score baseline preview.",
    )

    st.markdown("#### Selected AI approach")
    st.write(
        "The project will use an anomaly detector for unusual Bitcoin block inter-arrival times. "
        "The expected baseline is exponential waiting time between blocks, with a simple z-score preview now and an Isolation Forest evaluation planned for the final version."
    )

    try:
        blocks_df = load_anomaly_preview()
    except BlockchainApiError as exc:
        st.error(f"Could not load data for the AI module skeleton after trying the configured public APIs: {exc}")
        return
    except Exception as exc:
        st.error(f"Unexpected error in the AI module skeleton: {exc}")
        return

    if blocks_df.empty:
        st.warning("Not enough block data to compute anomaly features yet.")
        return

    anomaly_count = int(blocks_df["is_candidate_anomaly"].sum())
    metric_col_1, metric_col_2, metric_col_3 = st.columns(3)
    metric_col_1.metric("Training sample preview", f"{len(blocks_df):,} intervals")
    metric_col_2.metric("Mean interval", f"{blocks_df['minutes_since_prev'].mean():.2f} min")
    metric_col_3.metric("Candidate anomalies", anomaly_count)

    fig = px.scatter(
        blocks_df,
        x="timestamp_dt",
        y="minutes_since_prev",
        color="is_candidate_anomaly",
        title="Baseline anomaly preview for recent block intervals",
        labels={
            "timestamp_dt": "Block timestamp (UTC)",
            "minutes_since_prev": "Minutes since previous block",
            "is_candidate_anomaly": "Candidate anomaly",
        },
        hover_data={"height": True, "z_score": ":.2f", "id": True},
    )
    fig.add_hline(
        y=10,
        line_dash="dash",
        line_color="firebrick",
        annotation_text="10-minute target",
    )
    st.plotly_chart(style_chart(fig, height=430), width="stretch")

    st.markdown("#### Final model plan")
    st.dataframe(
        pd.DataFrame(
            [
                ("Data", "Recent and historical Bitcoin block timestamps from Blockstream"),
                ("Features", "Inter-arrival time, rolling mean, rolling standard deviation, period position"),
                ("Baseline", "Z-score threshold on block interval minutes"),
                ("Model", "Isolation Forest for unsupervised anomaly detection"),
                ("Evaluation", "Compare flagged events against statistical tail thresholds and report anomaly rate"),
            ],
            columns=["Area", "Planned implementation"],
        ),
        width="stretch",
        hide_index=True,
    )

    st.info("This module is intentionally a checkpoint skeleton for 29 April; the final evaluated model is due later.")
