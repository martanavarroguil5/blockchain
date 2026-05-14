from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from api.blockchain_client import BlockchainApiError, get_client
from modules.ui import anomaly_card_grid, concept_flow, module_header, story_panel, style_chart, styled_table, takeaway


TARGET_BLOCK_MINUTES = 10.0
DEFAULT_BLOCK_LIMIT = 240
MIN_MODEL_INTERVALS = 40
FEATURE_COLUMNS = [
    "minutes_since_prev",
    "absolute_target_deviation",
    "rolling_mean_12",
    "rolling_std_12",
    "rolling_z_score",
    "period_position",
    "negative_timestamp_jump",
]


@st.cache_data(ttl=300, show_spinner=False)
def load_anomaly_features(block_limit: int = DEFAULT_BLOCK_LIMIT) -> pd.DataFrame:
    client = get_client()
    recent_blocks = client.get_recent_blocks_window(limit=block_limit)
    blocks_df = pd.DataFrame(recent_blocks).sort_values("height").reset_index(drop=True)
    blocks_df["timestamp_dt"] = pd.to_datetime(blocks_df["timestamp"], unit="s", utc=True)
    blocks_df["minutes_since_prev"] = blocks_df["timestamp"].diff() / 60
    blocks_df = blocks_df.dropna(subset=["minutes_since_prev"]).copy()

    intervals = blocks_df["minutes_since_prev"]
    mean_interval = intervals.mean()
    std_interval = intervals.std(ddof=1)
    if std_interval == 0 or not np.isfinite(std_interval):
        blocks_df["z_score"] = 0.0
    else:
        blocks_df["z_score"] = (intervals - mean_interval) / std_interval

    rolling_mean = intervals.rolling(window=12, min_periods=3).mean()
    rolling_std = intervals.rolling(window=12, min_periods=3).std(ddof=1)
    expanding_mean = intervals.expanding(min_periods=1).mean()
    fallback_std = std_interval if np.isfinite(std_interval) and std_interval > 0 else 1.0

    blocks_df["absolute_target_deviation"] = (intervals - TARGET_BLOCK_MINUTES).abs()
    blocks_df["rolling_mean_12"] = rolling_mean.fillna(expanding_mean)
    blocks_df["rolling_std_12"] = rolling_std.replace(0, np.nan).fillna(fallback_std)
    blocks_df["rolling_z_score"] = (
        (intervals - blocks_df["rolling_mean_12"]) / blocks_df["rolling_std_12"]
    ).replace([np.inf, -np.inf], 0)
    blocks_df["period_position"] = (blocks_df["height"].astype(int) % 2016) / 2016
    blocks_df["negative_timestamp_jump"] = (intervals < 0).astype(int)
    blocks_df["baseline_anomaly"] = blocks_df["z_score"].abs() >= 2.5

    return blocks_df


def run_isolation_forest(blocks_df: pd.DataFrame, contamination: float) -> pd.DataFrame:
    try:
        from sklearn.ensemble import IsolationForest
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import RobustScaler
    except ImportError as exc:
        raise RuntimeError(
            "scikit-learn is required for the Isolation Forest model. Install the project requirements first."
        ) from exc

    model_df = blocks_df.copy()
    feature_frame = model_df[FEATURE_COLUMNS].replace([np.inf, -np.inf], np.nan)
    feature_frame = feature_frame.fillna(feature_frame.median(numeric_only=True)).fillna(0)

    model = make_pipeline(
        RobustScaler(),
        IsolationForest(
            n_estimators=250,
            contamination=contamination,
            random_state=42,
        ),
    )
    predictions = model.fit_predict(feature_frame)
    model_df["isolation_score"] = model.named_steps["isolationforest"].score_samples(
        model.named_steps["robustscaler"].transform(feature_frame)
    )
    model_df["model_anomaly"] = predictions == -1
    model_df["anomaly_label"] = np.where(
        model_df["model_anomaly"],
        "Isolation Forest anomaly",
        np.where(model_df["baseline_anomaly"], "z-score only", "Normal"),
    )
    return model_df


def _format_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def _explain_anomaly(row: pd.Series) -> tuple[str, str, list[str]]:
    interval = float(row["minutes_since_prev"])
    deviation = float(row["absolute_target_deviation"])
    z_score = float(row["z_score"])
    rolling_z = float(row["rolling_z_score"])
    score = float(row["isolation_score"])

    if interval >= TARGET_BLOCK_MINUTES * 2:
        title = "Long wait between blocks"
        core = (
            f"This block arrived after {interval:.2f} minutes, more than twice the 10-minute target. "
            "It does not imply the block is invalid, but it does mark an uncomfortable wait for the network."
        )
    elif interval <= TARGET_BLOCK_MINUTES * 0.35:
        title = "Very fast block"
        core = (
            f"This block appeared in {interval:.2f} minutes. This can happen by chance, but the model reviews it because it is far from the expected rhythm."
        )
    else:
        title = "Contextual rarity"
        core = (
            f"The interval was {interval:.2f} minutes. It does not look extreme by itself, but combined with recent context the model considers it unusual."
        )

    reasons = [
        f"Deviation from target: {deviation:.2f} minutes.",
        f"global z-score: {z_score:.2f}; local z-score: {rolling_z:.2f}.",
        f"Isolation Forest score: {score:.4f}; the lower it is, the rarer it is for the model.",
    ]
    if bool(row.get("negative_timestamp_jump", False)):
        reasons.append("The timestamp moves backward compared with the previous block, so it deserves additional review.")
    return title, core, reasons


def render_m4() -> None:
    module_header(
        "AI anomalies",
        "AI to detect unusual times",
        "An interpretable pipeline that turns block intervals into investigation signals.",
    )

    story_panel(
        "What anomaly means here",
        "An anomaly does not mean fraud or an invalid block.",
        "It means the time interval between blocks behaves unusually compared with recent context and the 10-minute target. "
        "The model is used to prioritize review: it points to where to look first, but it does not deliver a verdict.",
        [
            "The z-score marks extreme values in a simple, explainable way.",
            "Isolation Forest combines several signals to detect contextual rarity.",
            "Evaluation focuses on anomaly rate, overlap with the baseline, and the candidate table.",
        ],
    )
    concept_flow(
        [
            ("Data", "Recent blocks are taken and the time since the previous block is calculated."),
            ("Features", "Deviation variables, moving averages, local volatility, and position inside the difficulty period are created."),
            ("Baseline", "The z-score separates intervals that are far from the global mean."),
            ("Model", "Isolation Forest learns which points are rare by comparing them with the rest of the sample."),
        ]
    )

    block_limit = st.slider(
        "Historical block sample",
        min_value=80,
        max_value=400,
        value=DEFAULT_BLOCK_LIMIT,
        step=40,
        help="Higher values give the model more context, but require more calls to public sources.",
    )
    contamination = st.slider(
        "Expected anomaly rate",
        min_value=0.01,
        max_value=0.10,
        value=0.04,
        step=0.01,
        format="%.2f",
        help="Isolation Forest uses this value as the approximate percentage of intervals to flag.",
    )

    try:
        blocks_df = load_anomaly_features(block_limit)
    except BlockchainApiError as exc:
        st.error(f"Could not load public data for the AI analysis: {exc}")
        return
    except Exception as exc:
        st.error(f"Unexpected error while preparing AI variables: {exc}")
        return

    if blocks_df.empty:
        st.info("There are not enough blocks yet to calculate anomaly variables.")
        return

    if len(blocks_df) < MIN_MODEL_INTERVALS:
        st.info(f"At least {MIN_MODEL_INTERVALS} intervals are needed to train the Isolation Forest model.")
        return

    try:
        results_df = run_isolation_forest(blocks_df, contamination)
    except RuntimeError as exc:
        st.error(str(exc))
        return
    except Exception as exc:
        st.error(f"Unexpected error while training Isolation Forest: {exc}")
        return

    baseline_count = int(results_df["baseline_anomaly"].sum())
    model_count = int(results_df["model_anomaly"].sum())
    overlap_count = int((results_df["baseline_anomaly"] & results_df["model_anomaly"]).sum())
    anomaly_rate = model_count / len(results_df)

    metric_col_1, metric_col_2, metric_col_3, metric_col_4 = st.columns(4)
    metric_col_1.metric("Model sample", f"{len(results_df):,}")
    metric_col_2.metric("Average interval", f"{results_df['minutes_since_prev'].mean():.2f} min")
    metric_col_3.metric("AI anomalies", model_count, delta=_format_percent(anomaly_rate))
    metric_col_4.metric("Baseline overlap", f"{overlap_count}/{max(baseline_count, 1)}")
    st.write(
        "The z-score detects globally extreme intervals. Isolation Forest adds context: it looks at several variables at once and can flag a block "
        "because its local pattern is unusual, even if one single number does not look dramatic."
    )

    plot_df = results_df.copy()
    plot_df["block_hash_short"] = plot_df["id"].astype(str).str.slice(0, 6) + "..." + plot_df["id"].astype(str).str.slice(-6)
    plot_df["timestamp_label"] = plot_df["timestamp_dt"].dt.strftime("%Y-%m-%d %H:%M UTC")
    plot_df["tooltip_label"] = plot_df["anomaly_label"].replace(
        {
            "Isolation Forest anomaly": "AI candidate",
            "z-score only": "Statistical extreme",
        }
    )
    plot_df["tooltip_hint"] = np.select(
        [
            plot_df["model_anomaly"],
            plot_df["baseline_anomaly"],
        ],
        [
            "High priority for review",
            "Extreme interval by z-score",
        ],
        default="Expected behavior",
    )

    fig = px.scatter(
        plot_df,
        x="timestamp_dt",
        y="minutes_since_prev",
        color="anomaly_label",
        size="absolute_target_deviation",
        color_discrete_map={
            "Normal": "#0B7285",
            "z-score only": "#E8590C",
            "Isolation Forest anomaly": "#364FC7",
        },
        title="Block intervals and detected anomalies",
        labels={
            "timestamp_dt": "Block timestamp (UTC)",
            "minutes_since_prev": "Minutes since previous block",
            "anomaly_label": "Classification",
            "absolute_target_deviation": "Deviation from 10 min",
        },
        custom_data=[
            "tooltip_label",
            "timestamp_label",
            "height",
            "absolute_target_deviation",
            "z_score",
            "rolling_z_score",
            "isolation_score",
            "block_hash_short",
            "tooltip_hint",
        ],
    )
    fig.update_traces(
        marker={
            "line": {"width": 1.6, "color": "rgba(255,255,255,0.92)"},
            "opacity": 0.86,
        },
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "%{customdata[8]}<br><br>"
            "Block %{customdata[2]:,}<br>"
            "%{customdata[1]}<br>"
            "Interval: <b>%{y:.2f} min</b><br>"
            "Deviation from target: %{customdata[3]:.2f} min<br>"
            "global/local z-score: %{customdata[4]:.2f} / %{customdata[5]:.2f}<br>"
            "AI score: %{customdata[6]:.4f}<br>"
            "Short hash: %{customdata[7]}"
            "<extra></extra>"
        ),
    )
    fig.add_hline(
        y=TARGET_BLOCK_MINUTES,
        line_dash="dash",
        line_color="#0B7285",
        annotation_text="10 min target",
    )
    st.plotly_chart(style_chart(fig, height=430), width="stretch", config={"displayModeBar": False})
    st.write(
        "Each point is the time gap between two consecutive blocks. Larger points are farther from the 10-minute target. "
        "Points marked as anomalies are the candidates worth reviewing first."
    )

    comparison_col, feature_col = st.columns([1, 1])
    with comparison_col:
        st.markdown("#### Interpretable evaluation")
        st.write(
            "There is no official label for a 'real anomaly' in these intervals, so evaluation checks whether the model behaves sensibly: "
            "how many cases it marks, how much it overlaps with the baseline, and whether it detects striking timing situations."
        )
        styled_table(
            pd.DataFrame(
                [
                    ("z-score anomalies", baseline_count),
                    ("Isolation Forest anomalies", model_count),
                    ("Cases shared by both methods", overlap_count),
                    ("Model anomaly rate", _format_percent(anomaly_rate)),
                    ("Flagged negative timestamp jumps", int(results_df.loc[results_df["model_anomaly"], "negative_timestamp_jump"].sum())),
                ],
                columns=["Metric", "Value"],
            )
        )

    with feature_col:
        st.markdown("#### Variables used by the model")
        styled_table(
            pd.DataFrame(
                [
                    ("minutes_since_prev", "Observed interval between consecutive blocks"),
                    ("absolute_target_deviation", "Distance from the 10-minute target"),
                    ("rolling_mean_12", "Local context of recent timings"),
                    ("rolling_std_12", "Local volatility of intervals"),
                    ("rolling_z_score", "Standardized surprise in the nearby context"),
                    ("period_position", "Position within the 2016-block adjustment period"),
                    ("negative_timestamp_jump", "The header timestamp moves backward"),
                ],
                columns=["Variable", "Meaning"],
            )
        )

    st.markdown("#### Priority candidates")
    st.write(
        "The table is sorted by `isolation_score`. The lower the score, the rarer the case looks to the model, so the first rows are the most interesting."
    )
    story_panel(
        "Before reading the table",
        "What the rarity indicators mean",
        "The `z-score` measures how far an interval is from normal: large positive or negative values indicate unusual waiting times. "
        "The `local z-score` makes a similar comparison, but using the nearby context of recent blocks. "
        "The `AI score` comes from Isolation Forest: it is not a probability, but a rarity score; the lower it is, the more suspicious it looks to the model.",
        [
            "A candidate does not mean an attack or invalid block.",
            "It means that interval deserves to be explained or reviewed before others.",
            "The human reading turns those numbers into a defensible sentence for the presentation.",
        ],
    )
    anomaly_table = results_df.loc[results_df["model_anomaly"]].copy()
    if anomaly_table.empty:
        st.success("The current sample produced no anomaly candidates.")
    else:
        anomaly_table = anomaly_table.sort_values("isolation_score")
        explanation_candidates = anomaly_table.head(3).copy()
        anomaly_table = anomaly_table.head(12)
        anomaly_table["timestamp_dt"] = anomaly_table["timestamp_dt"].dt.strftime("%Y-%m-%d %H:%M UTC")
        anomaly_table["short_hash"] = anomaly_table["id"].astype(str).str.slice(0, 6) + "..." + anomaly_table["id"].astype(str).str.slice(-6)
        anomaly_table["minutes_since_prev"] = anomaly_table["minutes_since_prev"].map(lambda value: f"{float(value):.2f} min")
        anomaly_table["z_score"] = anomaly_table["z_score"].map(lambda value: f"{float(value):.2f}")
        anomaly_table["rolling_z_score"] = anomaly_table["rolling_z_score"].map(lambda value: f"{float(value):.2f}")
        anomaly_table["isolation_score"] = anomaly_table["isolation_score"].map(lambda value: f"{float(value):.4f}")
        styled_table(
            anomaly_table.rename(
                columns={
                    "height": "Block",
                    "timestamp_dt": "Date",
                    "minutes_since_prev": "Interval",
                    "z_score": "z-score",
                    "rolling_z_score": "local z-score",
                    "isolation_score": "AI score",
                    "short_hash": "Short hash",
                }
            )[
                [
                    "Block",
                    "Date",
                    "Interval",
                    "z-score",
                    "local z-score",
                    "AI score",
                    "Short hash",
                ]
            ]
        )
        st.markdown("#### Human reading of candidates")
        st.write(
            "These cards translate the model output into a defensible explanation: what happened, why it stands out, and which data point is worth checking."
        )
        anomaly_cards: list[tuple[str, str, str, list[str]]] = []
        for _, candidate in explanation_candidates.iterrows():
            title, body, reasons = _explain_anomaly(candidate)
            anomaly_cards.append(
                (
                    f"Block {int(candidate['height']):,}",
                    title,
                    body,
                    reasons,
                )
            )
        anomaly_card_grid(anomaly_cards)

    st.markdown("#### Model result")
    styled_table(
        pd.DataFrame(
            [
                ("Data", "Recent Bitcoin block timestamps from Blockstream with fallback to Mempool.space"),
                ("Baseline", "Global z-score threshold of 2.5 standard deviations"),
                ("Model", "Isolation Forest with robustly scaled timing variables"),
                ("Evaluation", "Anomaly rate, overlap with statistical tails, and candidate ranking"),
                ("Limitation", "Without real labels, the result is anomaly discovery, not supervised accuracy"),
            ],
            columns=["Area", "Implementation"],
        )
    )

    if overlap_count > 0:
        takeaway(
            "The model is working and partially overlaps with the baseline.",
            "That overlap helps explain the result: some candidates are also extreme under a simple statistical rule.",
            tone="success",
        )
    else:
        takeaway(
            "The model is working, but it is detecting contextual rarity.",
            "In this sample, Isolation Forest does not overlap with the global z-score. That can happen when rarity is not one isolated value, but the combination of context and timing.",
            tone="warning",
        )
