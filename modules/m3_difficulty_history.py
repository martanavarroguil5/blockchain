from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from api.blockchain_client import BlockchainApiError, get_client


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
    st.subheader("M3 - Difficulty History")
    st.caption("Completed Bitcoin difficulty adjustment periods from live Blockstream data.")

    period_count = st.slider(
        "Adjustment periods",
        min_value=4,
        max_value=12,
        value=8,
        step=1,
        help="One Bitcoin adjustment period is 2016 blocks.",
    )

    try:
        periods_df = load_difficulty_periods(period_count)
    except BlockchainApiError as exc:
        st.error(f"Could not load difficulty history: {exc}")
        return
    except Exception as exc:
        st.error(f"Unexpected error while building difficulty history: {exc}")
        return

    if periods_df.empty:
        st.warning("No completed adjustment periods were available from the API response.")
        return

    latest_row = periods_df.iloc[-1]
    metric_col_1, metric_col_2, metric_col_3 = st.columns(3)
    metric_col_1.metric("Latest completed period", f"{int(latest_row['period_index']):,}")
    metric_col_2.metric("Latest period difficulty", f"{float(latest_row['difficulty']):,.2f}")
    metric_col_3.metric(
        "Latest avg block time",
        f"{float(latest_row['average_block_minutes']):.2f} min",
        delta=f"{(float(latest_row['actual_vs_target_ratio']) - 1) * 100:+.1f}% vs target",
    )

    difficulty_fig = px.line(
        periods_df,
        x="period_start",
        y="difficulty",
        markers=True,
        title="Bitcoin difficulty at each adjustment event",
        labels={
            "period_start": "Adjustment event date (UTC)",
            "difficulty": "Difficulty",
        },
    )
    for row in periods_df.itertuples():
        difficulty_fig.add_vline(x=row.period_start, line_dash="dot", line_color="rgba(80,80,80,0.35)")
    st.plotly_chart(difficulty_fig, width="stretch")

    ratio_fig = px.bar(
        periods_df,
        x="period_start",
        y="actual_vs_target_ratio",
        title="Actual period duration compared with the 600-second target",
        labels={
            "period_start": "Period start (UTC)",
            "actual_vs_target_ratio": "Actual / target duration",
        },
        hover_data={
            "start_height": True,
            "next_adjustment_height": True,
            "average_block_minutes": ":.2f",
            "actual_days": ":.2f",
            "target_days": ":.2f",
        },
    )
    ratio_fig.add_hline(
        y=1,
        line_dash="dash",
        line_color="firebrick",
        annotation_text="Target duration",
    )
    st.plotly_chart(ratio_fig, width="stretch")

    st.markdown("#### Adjustment period table")
    display_df = periods_df.copy()
    display_df["period_start"] = display_df["period_start"].dt.strftime("%Y-%m-%d")
    st.dataframe(
        display_df[
            [
                "period_index",
                "start_height",
                "next_adjustment_height",
                "period_start",
                "difficulty",
                "average_block_minutes",
                "actual_vs_target_ratio",
            ]
        ],
        width="stretch",
        hide_index=True,
    )

    st.info(
        "If blocks are mined faster than 10 minutes on average, the ratio falls below 1 and the next difficulty adjustment should increase the target difficulty. "
        "If blocks are slower, the ratio rises above 1 and the next adjustment should reduce difficulty."
    )
