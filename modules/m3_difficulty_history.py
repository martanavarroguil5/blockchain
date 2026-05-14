from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from api.blockchain_client import BlockchainApiError, get_client
from modules.bitcoin_math import human_difficulty
from modules.ui import concept_flow, module_header, story_panel, style_chart, styled_table, takeaway


BLOCKS_PER_ADJUSTMENT = 2016
TARGET_SECONDS_PER_BLOCK = 600


def _period_bounds(latest_height: int, periods: int) -> list[tuple[int, int, int]]:
    latest_completed_period = latest_height // BLOCKS_PER_ADJUSTMENT - 1
    first_period = max(0, latest_completed_period - periods + 1)
    return [
        (
            period_index,
            period_index * BLOCKS_PER_ADJUSTMENT,
            (period_index + 1) * BLOCKS_PER_ADJUSTMENT,
        )
        for period_index in range(first_period, latest_completed_period + 1)
    ]


@st.cache_data(ttl=600, show_spinner=False)
def load_difficulty_periods(periods: int = 8) -> pd.DataFrame:
    client = get_client()
    latest_block = client.get_latest_block()
    latest_height = int(latest_block["height"])

    rows: list[dict[str, object]] = []
    for period_index, start_height, next_start_height in _period_bounds(latest_height, periods):
        start_block = client.get_block_by_height(start_height)
        next_period_block = client.get_block_by_height(next_start_height)
        elapsed_seconds = int(next_period_block["timestamp"]) - int(start_block["timestamp"])
        expected_seconds = BLOCKS_PER_ADJUSTMENT * TARGET_SECONDS_PER_BLOCK

        rows.append(
            {
                "period_index": period_index,
                "start_height": start_height,
                "next_adjustment_height": next_start_height,
                "period_start": datetime.fromtimestamp(int(start_block["timestamp"]), UTC),
                "difficulty": float(start_block["difficulty"]),
                "actual_days": elapsed_seconds / 86_400,
                "target_days": expected_seconds / 86_400,
                "actual_vs_target_ratio": elapsed_seconds / expected_seconds,
                "average_block_minutes": elapsed_seconds / BLOCKS_PER_ADJUSTMENT / 60,
            }
        )

    return pd.DataFrame(rows)


def render_m3() -> None:
    module_header(
        "Difficulty",
        "Difficulty as an autopilot",
        "Recent adjustment periods and comparison between real time and the 10-minute target.",
    )
    story_panel(
        "The problem it solves",
        "Bitcoin needs blocks to appear neither too fast nor too slow.",
        "Because mining power changes constantly, the network cannot set one difficulty forever. "
        "Every 2016 blocks, it compares real elapsed time with expected time and adjusts difficulty to return to the 10-minute-per-block rhythm.",
        [
            "If blocks arrive too fast, difficulty tends to rise.",
            "If blocks arrive too slowly, difficulty tends to fall.",
            "The adjustment does not react to one isolated block, but to a full period.",
        ],
    )
    concept_flow(
        [
            (
                "Choose sample",
                "Select how many complete adjustment periods to inspect. Each period has 2016 blocks, about two weeks.",
            ),
            (
                "Measure time",
                "For each period, the initial block and the next adjustment block are queried, and the real elapsed time is calculated.",
            ),
            (
                "Compare",
                "That real time is compared with the theoretical target: 2016 blocks times 10 minutes each.",
            ),
            (
                "Interpret",
                "If the period was fast, difficulty tends to rise; if it was slow, it tends to fall.",
            ),
        ]
    )

    control_col, context_col = st.columns([1, 2.2])
    with control_col:
        period_count = st.selectbox(
            "Analyzed periods",
            [4, 6, 8, 10, 12],
            index=2,
            format_func=lambda value: f"{value} periods",
            help="More periods give more historical context, but require more calls to public APIs.",
        )
    with context_col:
        st.markdown("#### What this selector changes")
        st.write(
            "Each period contains 2016 blocks. If you choose more periods, the chart looks at more history; "
            "if you choose fewer, it focuses on the most recent adjustments. Changing it queries public data again."
        )

    try:
        with st.spinner("Querying the start and end blocks of each period..."):
            periods_df = load_difficulty_periods(period_count)
    except BlockchainApiError as exc:
        st.error(f"Could not load difficulty history from public sources: {exc}")
        return
    except Exception as exc:
        st.error(f"Unexpected error while preparing difficulty history: {exc}")
        return

    if periods_df.empty:
        st.info("No complete adjustment periods are available in the current response.")
        return

    latest_row = periods_df.iloc[-1]
    metric_col_1, metric_col_2, metric_col_3 = st.columns(3)
    metric_col_1.metric("Latest complete period", f"{int(latest_row['period_index']):,}")
    metric_col_2.metric("Period difficulty", human_difficulty(float(latest_row["difficulty"])))
    metric_col_3.metric(
        "Average per block",
        f"{float(latest_row['average_block_minutes']):.2f} min",
        delta=f"{(float(latest_row['actual_vs_target_ratio']) - 1) * 100:+.1f}% vs target",
    )

    chart_df = periods_df.copy()
    chart_df["difficulty_label"] = chart_df["difficulty"].map(lambda value: human_difficulty(float(value)))
    chart_df["period_start_label"] = chart_df["period_start"].dt.strftime("%Y-%m-%d")

    difficulty_fig = px.line(
        chart_df,
        x="period_start",
        y="difficulty",
        markers=True,
        title="Bitcoin difficulty at each adjustment event",
        labels={
            "period_start": "Adjustment date (UTC)",
            "difficulty": "Difficulty",
        },
        custom_data=["period_index", "period_start_label", "difficulty_label", "average_block_minutes"],
    )
    difficulty_fig.update_traces(
        line={"width": 3, "color": "#0B7285"},
        marker={"size": 10, "color": "#364FC7", "line": {"width": 2, "color": "#ffffff"}},
        hovertemplate=(
            "<b>Adjustment %{customdata[0]:,}</b><br>"
            "Date: %{customdata[1]}<br>"
            "Difficulty: %{customdata[2]}<br>"
            "Average per block: %{customdata[3]:.2f} min"
            "<extra></extra>"
        ),
    )
    for row in periods_df.itertuples():
        difficulty_fig.add_vline(x=row.period_start, line_dash="dot", line_color="rgba(80,80,80,0.35)")
    st.markdown("#### Chart 1: how difficulty changes")
    st.write(
        "Each point represents the difficulty active at the start of a 2016-block period. "
        "The line rises when Bitcoin makes the search for valid hashes harder and falls when it eases it. "
        "Vertical lines mark adjustment events."
    )
    st.plotly_chart(style_chart(difficulty_fig, height=430), width="stretch", config={"displayModeBar": False})

    ratio_fig = px.bar(
        chart_df,
        x="period_start",
        y="actual_vs_target_ratio",
        title="Real period duration versus target",
        labels={
            "period_start": "Period start (UTC)",
            "actual_vs_target_ratio": "Real duration / target",
        },
        custom_data=[
            "period_index",
            "period_start_label",
            "start_height",
            "next_adjustment_height",
            "average_block_minutes",
            "actual_days",
            "target_days",
        ],
    )
    ratio_fig.update_traces(
        marker_color="#0B7285",
        marker_line_color="rgba(255,255,255,0.9)",
        marker_line_width=1.2,
        hovertemplate=(
            "<b>Period %{customdata[0]:,}</b><br>"
            "Start: %{customdata[1]}<br>"
            "Heights: %{customdata[2]:,} to %{customdata[3]:,}<br>"
            "Real/target ratio: %{y:.3f}<br>"
            "Average per block: %{customdata[4]:.2f} min<br>"
            "Real duration: %{customdata[5]:.2f} days<br>"
            "Target: %{customdata[6]:.2f} days"
            "<extra></extra>"
        ),
    )
    ratio_fig.add_hline(
        y=1,
        line_dash="dash",
        line_color="#0B7285",
        annotation_text="Target",
    )
    st.markdown("#### Chart 2: whether blocks were fast or slow")
    st.write(
        "This chart calculates the real duration of each period and divides it by the expected duration. "
        "The ideal value is 1: it means the period lasted as expected. Below 1, blocks arrived faster; "
        "above 1, they arrived slower."
    )
    st.plotly_chart(style_chart(ratio_fig, height=420), width="stretch", config={"displayModeBar": False})

    st.markdown("#### Auditable period table")
    st.write(
        "Each row represents a complete 2016-block period. This lets you check where the charts come from: initial height, next adjustment, and average time per block."
    )
    display_df = periods_df.copy()
    display_df["Date"] = display_df["period_start"].dt.strftime("%Y-%m-%d")
    display_df["Difficulty"] = display_df["difficulty"].map(lambda value: human_difficulty(float(value)))
    display_df["Average per block"] = display_df["average_block_minutes"].map(lambda value: f"{float(value):.2f} min")
    display_df["Real/target ratio"] = display_df["actual_vs_target_ratio"].map(lambda value: f"{float(value):.3f}")
    styled_table(
        display_df.rename(
            columns={
                "period_index": "Period",
                "start_height": "Start height",
                "next_adjustment_height": "Next adjustment",
            }
        )[
            [
                "Period",
                "Start height",
                "Next adjustment",
                "Date",
                "Difficulty",
                "Average per block",
                "Real/target ratio",
            ]
        ]
    )

    st.info(
        "Reading rule: a ratio below 1 means the period was faster than the theoretical schedule; a ratio above 1 means it was slower."
    )

    latest_ratio = float(latest_row["actual_vs_target_ratio"])
    if latest_ratio < 0.98:
        takeaway(
            "The latest period was faster than the target.",
            "This suggests effective mining power was high during that period. The expected protocol response is to harden difficulty.",
            tone="warning",
        )
    elif latest_ratio > 1.02:
        takeaway(
            "The latest period was slower than the target.",
            "This suggests effective mining power was lower or less efficient. The expected response is to soften difficulty.",
            tone="warning",
        )
    else:
        takeaway(
            "The latest period stayed close to the theoretical schedule.",
            "The real duration is fairly aligned with the two-week target for every 2016 blocks.",
            tone="success",
        )
