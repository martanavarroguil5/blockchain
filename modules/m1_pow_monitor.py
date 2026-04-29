from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from api.blockchain_client import BlockchainApiError, get_client
from modules.bitcoin_math import (
    bits_to_target,
    estimate_hash_rate_hs,
    human_difficulty,
    human_hash_rate,
    leading_zero_bits,
)
from modules.ui import module_header, style_chart


@st.cache_data(ttl=60, show_spinner=False)
def load_pow_snapshot(block_limit: int = 40) -> dict[str, object]:
    client = get_client()
    latest_block = client.get_latest_block()
    recent_blocks = client.get_recent_blocks_window(limit=block_limit)

    blocks_df = pd.DataFrame(recent_blocks).sort_values("height").reset_index(drop=True)
    blocks_df["timestamp_dt"] = pd.to_datetime(blocks_df["timestamp"], unit="s", utc=True)
    blocks_df["minutes_since_prev"] = blocks_df["timestamp"].diff() / 60

    latest_bits = int(latest_block["bits"])
    target = bits_to_target(latest_bits)
    hash_rate_hs = estimate_hash_rate_hs(float(latest_block["difficulty"]))

    return {
        "latest_block": latest_block,
        "recent_blocks": blocks_df,
        "target": target,
        "target_hex": f"{target:064x}",
        "target_leading_zero_bits": leading_zero_bits(target),
        "hash_rate_hs": hash_rate_hs,
    }


def render_m1() -> None:
    st_autorefresh(interval=60_000, key="m1_autorefresh")
    module_header(
        "Module 1",
        "Proof of Work Monitor",
        "Live mining metrics, target threshold, estimated hash rate, and recent block timing behavior.",
    )

    try:
        snapshot = load_pow_snapshot()
    except BlockchainApiError as exc:
        st.error(f"Could not load blockchain data after trying the configured public APIs: {exc}")
        return
    except Exception as exc:
        st.error(f"Unexpected error while building M1: {exc}")
        return

    latest_block = snapshot["latest_block"]
    recent_blocks = snapshot["recent_blocks"]
    if not isinstance(latest_block, dict) or not isinstance(recent_blocks, pd.DataFrame):
        st.error("Unexpected data format returned by the blockchain client.")
        return

    now_utc = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    st.caption(f"Snapshot generated at {now_utc}. Auto-refresh interval: 60 seconds.")

    metric_col_1, metric_col_2, metric_col_3, metric_col_4 = st.columns(4)
    metric_col_1.metric("Latest block height", f"{int(latest_block['height']):,}")
    metric_col_2.metric("Difficulty", human_difficulty(float(latest_block["difficulty"])))
    metric_col_3.metric("Estimated hash rate", human_hash_rate(float(snapshot["hash_rate_hs"])))
    metric_col_4.metric("Transactions", f"{int(latest_block['tx_count']):,}")

    target_hex = str(snapshot["target_hex"])
    st.markdown("#### Difficulty as a SHA-256 target threshold")
    st.code(target_hex, language="text")
    st.write(
        f"The compact `bits` field is `{int(latest_block['bits'])}`. "
        f"It expands to a 256-bit target with approximately `{int(snapshot['target_leading_zero_bits'])}` leading zero bits."
    )

    clean_intervals = recent_blocks["minutes_since_prev"].dropna()
    if clean_intervals.empty:
        st.warning("Not enough recent blocks were loaded to compute inter-block times.")
        return

    interval_col, stats_col = st.columns([2, 1])
    with interval_col:
        interval_fig = px.histogram(
            recent_blocks.dropna(subset=["minutes_since_prev"]),
            x="minutes_since_prev",
            nbins=15,
            title="Distribution of time between recent blocks",
            labels={"minutes_since_prev": "Minutes between blocks"},
        )
        interval_fig.update_layout(bargap=0.08)
        st.plotly_chart(style_chart(interval_fig, height=420), width="stretch")

    with stats_col:
        st.markdown("#### Inter-block timing stats")
        st.metric("Mean interval", f"{clean_intervals.mean():.2f} min")
        st.metric("Median interval", f"{clean_intervals.median():.2f} min")
        st.metric("Std. deviation", f"{clean_intervals.std(ddof=1):.2f} min")
        st.metric("Coeff. of variation", f"{(clean_intervals.std(ddof=1) / clean_intervals.mean()):.2f}")
        st.info(
            "Bitcoin block arrivals are usually modeled as a Poisson process, so inter-arrival times are expected to follow an exponential distribution."
        )

    trend_fig = px.line(
        recent_blocks.dropna(subset=["minutes_since_prev"]),
        x="timestamp_dt",
        y="minutes_since_prev",
        markers=True,
        title="Recent block intervals over time",
        labels={
            "timestamp_dt": "Block timestamp (UTC)",
            "minutes_since_prev": "Minutes since previous block",
        },
    )
    trend_fig.add_hline(
        y=10,
        line_dash="dash",
        line_color="firebrick",
        annotation_text="10-minute target",
    )
    st.plotly_chart(style_chart(trend_fig, height=430), width="stretch")

    st.markdown("#### Latest block summary")
    st.json(
        {
            "hash": latest_block["id"],
            "previous_block_hash": latest_block["previousblockhash"],
            "nonce": latest_block["nonce"],
            "bits": latest_block["bits"],
            "difficulty": latest_block["difficulty"],
            "timestamp": latest_block["timestamp"],
        }
    )

    avg_interval_seconds = clean_intervals.mean() * 60
    deviation_ratio = avg_interval_seconds / 600
    st.write(
        "Observed average over the recent sample: "
        f"`{avg_interval_seconds:.1f}` seconds per block, "
        f"which is `{deviation_ratio:.2f}x` the ideal 600-second target."
    )

    if np.isfinite(deviation_ratio) and deviation_ratio > 1.25:
        st.warning("Recent block production is slower than the long-run Bitcoin target.")
    elif np.isfinite(deviation_ratio) and deviation_ratio < 0.75:
        st.warning("Recent block production is faster than the long-run Bitcoin target.")
    else:
        st.success("Recent block production is reasonably close to the long-run 10-minute target.")
