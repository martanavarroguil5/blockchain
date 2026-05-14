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
from modules.ui import health_grid, metric_explainer_grid, module_header, story_panel, style_chart, takeaway


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


def _classify_interval_health(deviation_ratio: float) -> tuple[str, str]:
    if not np.isfinite(deviation_ratio):
        return "No data", "watch"
    if 0.80 <= deviation_ratio <= 1.20:
        return "Normal", "good"
    if 0.60 <= deviation_ratio <= 1.45:
        return "Watch", "watch"
    return "Tension", "risk"


def _classify_activity(tx_count: int) -> tuple[str, str]:
    if tx_count >= 2_000:
        return "High", "good"
    if tx_count >= 500:
        return "Medium", "watch"
    return "Low", "risk"


def render_m1() -> None:
    st_autorefresh(interval=60_000, key="m1_autorefresh")
    module_header(
        "Live network",
        "The Bitcoin network right now",
        "Live metrics to understand how much work mining a block requires today.",
    )

    try:
        snapshot = load_pow_snapshot()
    except BlockchainApiError as exc:
        st.error(f"Could not load public Bitcoin data: {exc}")
        return
    except Exception as exc:
        st.error(f"Unexpected error while preparing this view: {exc}")
        return

    latest_block = snapshot["latest_block"]
    recent_blocks = snapshot["recent_blocks"]
    if not isinstance(latest_block, dict) or not isinstance(recent_blocks, pd.DataFrame):
        st.error("The data source returned an unexpected format.")
        return

    now_utc = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    st.caption(f"Snapshot generated at {now_utc}. Automatic refresh: 60 seconds.")
    story_panel(
        "Before reading the numbers",
        "What these metrics show",
        "This screen summarizes the current state of Bitcoin. Height tells us which block was accepted most recently; "
        "difficulty shows how demanding it is to find a valid hash; hash rate estimates how much computing power "
        "is competing on the network; and transactions show how much activity was included in that block. "
        "Together, these figures show whether the network is progressing normally and how much work supports each block.",
    )

    metric_explainer_grid(
        [
            (
                "Latest height",
                f"{int(latest_block['height']):,}",
                "Number of the latest block accepted by the network; it shows how far Bitcoin has advanced.",
            ),
            (
                "Difficulty",
                human_difficulty(float(latest_block["difficulty"])),
                "Multiplier versus the base level: 134 T means about 134 trillion times more attempts on average.",
            ),
            (
                "Estimated hash rate",
                human_hash_rate(float(snapshot["hash_rate_hs"])),
                "Approximate computing power competing on the network; higher values imply stronger economic security.",
            ),
            (
                "Transactions",
                f"{int(latest_block['tx_count']):,}",
                "Operations included in the latest block; it summarizes the activity confirmed in that piece of the chain.",
            ),
        ]
    )

    clean_intervals = recent_blocks["minutes_since_prev"].dropna()
    if not clean_intervals.empty:
        avg_interval_seconds = clean_intervals.mean() * 60
        deviation_ratio = avg_interval_seconds / 600
        interval_status, interval_tone = _classify_interval_health(deviation_ratio)
        activity_status, activity_tone = _classify_activity(int(latest_block["tx_count"]))
        st.markdown("#### Network health traffic light")
        st.write(
            "This summary turns the main metrics into a quick reading. It is not a definitive alert: it helps decide what to look at first."
        )
        story_panel(
            "How to read it",
            "The traffic light does not say whether Bitcoin is absolutely good or bad.",
            "It summarizes concrete signals from this recent sample. `Normal` means the value is close to what is expected; "
            "`Watch` means it is moving away a little; `Tension` marks a stronger deviation. For difficulty and hash rate, the reading is descriptive: "
            "it helps understand how much computational work supports the network at this moment.",
        )
        health_grid(
            [
                (
                    "Block rhythm",
                    interval_status,
                    f"Recent average: {clean_intervals.mean():.2f} min per block versus the 10 min target.",
                    interval_tone,
                ),
                (
                    "Difficulty",
                    "Hard target",
                    f"Current difficulty: {human_difficulty(float(latest_block['difficulty']))}. Fewer hashes satisfy the rule, so mining requires more attempts.",
                    "info",
                ),
                (
                    "Hash rate",
                    "Estimated power",
                    f"The network is trying around {human_hash_rate(float(snapshot['hash_rate_hs']))} in hash attempts.",
                    "good",
                ),
                (
                    "Activity",
                    activity_status,
                    f"The latest block included {int(latest_block['tx_count']):,} transactions.",
                    activity_tone,
                ),
            ]
        )

    target_hex = str(snapshot["target_hex"])
    st.markdown("#### Difficulty converted into a target")
    st.write(
        "Difficulty ultimately becomes a target number. A valid hash must be lower than that number. "
        "The smaller the target is, the smaller the space of acceptable hashes becomes."
    )
    st.code(target_hex, language="text")
    st.write(
        f"The compact block field `bits` is `{int(latest_block['bits'])}`. "
        f"Expanding it produces a 256-bit target with roughly `{int(snapshot['target_leading_zero_bits'])}` leading zero bits."
    )

    if clean_intervals.empty:
        st.info("There are not enough recent blocks yet to calculate intervals.")
        return

    interval_col, stats_col = st.columns([2, 1])
    with interval_col:
        st.markdown("#### How blocks are being spaced")
        st.write(
            "Bitcoin targets 10 minutes on average, but it does not promise exactly 10 minutes. "
            "This histogram shows whether recent blocks clustered near the target or had widely spread waiting times."
        )
        interval_fig = px.histogram(
            recent_blocks.dropna(subset=["minutes_since_prev"]),
            x="minutes_since_prev",
            nbins=15,
            title="Distribution of recent block intervals",
            labels={"minutes_since_prev": "Minutes between blocks"},
        )
        interval_fig.update_traces(
            marker_color="#0B7285",
            marker_line_color="rgba(255,255,255,0.9)",
            marker_line_width=1.1,
            hovertemplate=(
                "<b>Grouped intervals</b><br>"
                "Minutes: %{x:.2f}<br>"
                "Blocks in range: %{y}"
                "<extra></extra>"
            ),
        )
        interval_fig.update_yaxes(title_text="Blocks")
        interval_fig.update_layout(bargap=0.08)
        st.plotly_chart(style_chart(interval_fig, height=420), width="stretch", config={"displayModeBar": False})

    with stats_col:
        st.markdown("#### Timing summary")
        st.metric("Mean", f"{clean_intervals.mean():.2f} min")
        st.metric("Median", f"{clean_intervals.median():.2f} min")
        st.metric("Standard deviation", f"{clean_intervals.std(ddof=1):.2f} min")
        st.metric("Variation coeff.", f"{(clean_intervals.std(ddof=1) / clean_intervals.mean()):.2f}")
        st.info(
            "Blocks are usually modeled as a random process: normal behavior is not a perfect line, but a distribution of waiting times."
        )

    trend_df = recent_blocks.dropna(subset=["minutes_since_prev"]).copy()
    trend_df["timestamp_label"] = trend_df["timestamp_dt"].dt.strftime("%Y-%m-%d %H:%M UTC")
    trend_fig = px.line(
        trend_df,
        x="timestamp_dt",
        y="minutes_since_prev",
        markers=True,
        title="Recent intervals over time",
        labels={
            "timestamp_dt": "Block timestamp (UTC)",
            "minutes_since_prev": "Minutes since previous block",
        },
        custom_data=["height", "timestamp_label", "minutes_since_prev"],
    )
    trend_fig.update_traces(
        line={"width": 2.8, "color": "#0B7285"},
        marker={"size": 8, "color": "#364FC7", "line": {"width": 1.6, "color": "#ffffff"}},
        hovertemplate=(
            "<b>Block %{customdata[0]:,}</b><br>"
            "Date: %{customdata[1]}<br>"
            "Interval: %{customdata[2]:.2f} min<br>"
            "Target: 10.00 min"
            "<extra></extra>"
        ),
    )
    trend_fig.add_hline(
        y=10,
        line_dash="dash",
        line_color="#0B7285",
        annotation_text="Target 10 min",
    )
    st.plotly_chart(style_chart(trend_fig, height=430), width="stretch", config={"displayModeBar": False})
    st.write(
        "Points above the line took more than 10 minutes; points below it arrived faster. "
        "A short streak is not a problem: difficulty adjustment is the mechanism that corrects sustained deviations."
    )

    st.markdown("#### Reference block")
    st.write(
        "This summary connects the metrics with a real block. The hash and the `bits` field are verified in more detail in the block section."
    )
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
        "Observed average in the recent sample: "
        f"`{avg_interval_seconds:.1f}` seconds per block, "
        f"that is `{deviation_ratio:.2f}x` the ideal target of 600 seconds."
    )

    if np.isfinite(deviation_ratio) and deviation_ratio > 1.25:
        takeaway(
            "The recent sample is slow.",
            "The recent average is clearly above the target. If this situation lasted for a full period, the network would tend to lower difficulty.",
            tone="warning",
        )
    elif np.isfinite(deviation_ratio) and deviation_ratio < 0.75:
        takeaway(
            "The recent sample is fast.",
            "The recent average is clearly below the target. If it continued, the network would tend to raise difficulty.",
            tone="warning",
        )
    else:
        takeaway(
            "The recent sample is close to the target.",
            "Although individual blocks vary, the observed average is not far from 10 minutes per block.",
            tone="success",
        )
