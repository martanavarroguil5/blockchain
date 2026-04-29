from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st


COLORWAY = ["#0F766E", "#4F46E5", "#D97706", "#0891B2", "#7C3AED", "#16A34A"]


def apply_app_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #f5f7fb;
            --surface: #ffffff;
            --surface-soft: #eef4f7;
            --text: #0f172a;
            --muted: #526173;
            --border: #d8e1ec;
            --primary: #0f766e;
            --primary-dark: #115e59;
            --accent: #4f46e5;
            --warning: #b45309;
            --success: #15803d;
            --shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
        }

        .stApp {
            background:
                linear-gradient(180deg, rgba(238, 244, 247, 0.72), rgba(245, 247, 251, 0.96) 360px),
                var(--bg);
            color: var(--text);
        }

        .block-container {
            max-width: 1280px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        [data-testid="stSidebar"] {
            background: #0f172a;
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        [data-testid="stSidebar"] * {
            color: #e5eef8;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] li {
            color: #cbd5e1;
        }

        h1, h2, h3 {
            color: var(--text);
            letter-spacing: 0;
        }

        h1 {
            font-size: clamp(2rem, 4vw, 3.6rem);
            line-height: 1.04;
            margin-bottom: 0.3rem;
        }

        h2, h3 {
            margin-top: 0.8rem;
        }

        p, li, .stMarkdown {
            color: var(--muted);
            line-height: 1.6;
        }

        [data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem 1rem 0.95rem;
            box-shadow: var(--shadow);
        }

        [data-testid="stMetricLabel"] {
            color: var(--muted);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        [data-testid="stMetricValue"] {
            color: var(--text);
            font-weight: 750;
            font-variant-numeric: tabular-nums;
        }

        [data-testid="stTabs"] [role="tablist"] {
            gap: 0.4rem;
            border-bottom: 1px solid var(--border);
        }

        [data-testid="stTabs"] button[role="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 0.75rem 1rem;
        }

        [data-testid="stTabs"] button[aria-selected="true"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-bottom-color: var(--surface);
            color: var(--primary-dark);
            font-weight: 700;
        }

        [data-testid="stDataFrame"],
        [data-testid="stTable"],
        [data-testid="stJson"],
        [data-testid="stCodeBlock"],
        [data-testid="stPlotlyChart"] {
            border-radius: 8px;
        }

        [data-testid="stAlert"] {
            border-radius: 8px;
            border: 1px solid rgba(15, 23, 42, 0.08);
        }

        .hero-panel {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: clamp(1rem, 3vw, 1.6rem);
            box-shadow: var(--shadow);
            margin-bottom: 1.2rem;
        }

        .hero-eyebrow {
            color: var(--primary-dark);
            font-weight: 750;
            font-size: 0.82rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.45rem;
        }

        .hero-copy {
            max-width: 860px;
            color: var(--muted);
            font-size: 1.04rem;
            margin: 0.4rem 0 0;
        }

        .status-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 1rem;
        }

        .status-pill {
            align-items: center;
            background: #eef8f6;
            border: 1px solid #b8ded7;
            border-radius: 999px;
            color: var(--primary-dark);
            display: inline-flex;
            font-size: 0.82rem;
            font-weight: 700;
            min-height: 34px;
            padding: 0.35rem 0.72rem;
        }

        .status-pill.secondary {
            background: #eef2ff;
            border-color: #c7d2fe;
            color: #3730a3;
        }

        .status-pill.pending {
            background: #fff7ed;
            border-color: #fed7aa;
            color: #9a3412;
        }

        .module-heading {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            box-shadow: var(--shadow);
            margin: 0.9rem 0 1rem;
            padding: 1rem 1.1rem;
        }

        .module-kicker {
            color: var(--primary-dark);
            font-size: 0.78rem;
            font-weight: 750;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .module-heading h2 {
            margin: 0.15rem 0 0.2rem;
        }

        .module-heading p {
            margin: 0;
        }

        .insight-grid {
            display: grid;
            gap: 0.8rem;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            margin: 0.7rem 0 1.15rem;
        }

        .insight-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            box-shadow: var(--shadow);
            padding: 1rem;
        }

        .insight-label {
            color: var(--muted);
            font-size: 0.76rem;
            font-weight: 750;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }

        .insight-value {
            color: var(--text);
            font-size: 1.55rem;
            font-weight: 760;
            line-height: 1.2;
            margin-top: 0.32rem;
            overflow-wrap: anywhere;
        }

        .insight-note {
            color: var(--muted);
            font-size: 0.9rem;
            margin-top: 0.45rem;
        }

        code {
            border-radius: 6px;
        }

        @media (max-width: 760px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .hero-panel,
            .module-heading,
            .insight-card {
                box-shadow: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero() -> None:
    st.markdown(
        """
        <section class="hero-panel">
            <div class="hero-eyebrow">Bitcoin cryptography dashboard</div>
            <h1>CryptoChain Analyzer Dashboard</h1>
            <p class="hero-copy">
                Live proof-of-work metrics, local block header verification,
                difficulty history, and an AI anomaly detection pipeline for the Bitcoin network.
            </p>
            <div class="status-row">
                <span class="status-pill">M1 Operational</span>
                <span class="status-pill">M2 Operational</span>
                <span class="status-pill">M3 Operational</span>
                <span class="status-pill secondary">M4 Skeleton</span>
                <span class="status-pill pending">Checkpoint 29 Apr</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def module_header(kicker: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <section class="module-heading">
            <div class="module-kicker">{kicker}</div>
            <h2>{title}</h2>
            <p>{subtitle}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def insight_grid(items: list[tuple[str, str, str]]) -> None:
    cards = "".join(
        (
            '<article class="insight-card">'
            f'<div class="insight-label">{label}</div>'
            f'<div class="insight-value">{value}</div>'
            f'<div class="insight-note">{note}</div>'
            "</article>"
        )
        for label, value, note in items
    )
    st.markdown(f'<div class="insight-grid">{cards}</div>', unsafe_allow_html=True)


def style_chart(fig: go.Figure, *, height: int | None = None) -> go.Figure:
    fig.update_layout(
        colorway=COLORWAY,
        font={"family": "Inter, Segoe UI, Arial, sans-serif", "color": "#0f172a"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        margin={"l": 32, "r": 22, "t": 60, "b": 42},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
        },
        hoverlabel={
            "bgcolor": "#0f172a",
            "font_color": "#f8fafc",
            "bordercolor": "#0f172a",
        },
    )
    fig.update_xaxes(showgrid=True, gridcolor="#edf2f7", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#edf2f7", zeroline=False)
    if height is not None:
        fig.update_layout(height=height)
    return fig
