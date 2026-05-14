from __future__ import annotations

from html import escape

import plotly.graph_objects as go
import streamlit as st


COLORWAY = ["#0B7285", "#364FC7", "#2B8A3E", "#9C36B5", "#0CA678", "#F59F00"]


def apply_app_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #eef4f6;
            --surface: #ffffff;
            --surface-soft: #edf7f8;
            --ink: #0f172a;
            --text: #172033;
            --muted: #596579;
            --border: #dbe4ea;
            --primary: #0b7285;
            --primary-dark: #075463;
            --primary-soft: #e7f6f8;
            --accent: #364fc7;
            --accent-soft: #edf2ff;
            --blue-soft: #edf2ff;
            --success: #2b8a3e;
            --warning: #b7791f;
            --shadow: 0 30px 80px rgba(15, 23, 42, 0.18);
            --shadow-lift: 0 30px 70px rgba(11, 114, 133, 0.20), 0 14px 34px rgba(15, 23, 42, 0.14);
            --shadow-soft: 0 14px 34px rgba(15, 23, 42, 0.10);
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 6%, rgba(20, 184, 166, 0.22), transparent 330px),
                radial-gradient(circle at 88% 8%, rgba(54, 79, 199, 0.18), transparent 420px),
                linear-gradient(180deg, #dfecef 0, #f7fafb 320px, #eef4f6 100%),
                var(--bg);
            color: var(--text);
        }

        .block-container {
            max-width: 1280px;
            padding-top: 1.2rem;
            padding-bottom: 4rem;
        }

        .stApp * {
            text-rendering: optimizeLegibility;
        }

        [data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, #0f172a 0%, #111827 54%, #082f49 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.10);
            box-shadow: 12px 0 34px rgba(15, 23, 42, 0.16);
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

        h3, h4 {
            letter-spacing: 0;
        }

        h4 {
            color: var(--primary-dark);
            font-size: 1.05rem;
        }

        p, li, .stMarkdown {
            color: var(--muted);
            line-height: 1.6;
        }

        .stMarkdown strong {
            color: var(--text);
        }

        input[type="radio"],
        input[type="checkbox"],
        input[type="range"] {
            accent-color: var(--primary);
        }

        [data-testid="stRadio"] [role="radiogroup"] {
            background: rgba(255, 255, 255, 0.72);
            border: 1px solid rgba(219, 228, 234, 0.88);
            border-radius: 8px;
            box-shadow: var(--shadow-soft);
            gap: 0.45rem;
            padding: 0.45rem;
        }

        [data-testid="stRadio"] label {
            background: transparent;
            border: 1px solid transparent;
            border-radius: 8px;
            min-height: 42px;
            padding: 0.22rem 0.9rem;
            transition: background-color 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
        }

        [data-testid="stRadio"] label input[type="radio"] {
            opacity: 0;
            position: absolute;
            pointer-events: none;
        }

        [data-testid="stRadio"] label > div:first-child {
            display: none !important;
        }

        [data-testid="stRadio"] label:has(input:checked) {
            background: linear-gradient(135deg, #e6fbff, #eef2ff);
            border-color: #73cbd7;
            box-shadow: 0 12px 28px rgba(11, 114, 133, 0.18), inset 0 0 0 1px rgba(11, 114, 133, 0.22);
        }

        [data-testid="stRadio"] label:has(input:checked) p {
            color: var(--primary-dark);
            font-weight: 760;
        }

        [data-testid="stSelectbox"] [data-baseweb="select"] > div {
            background: rgba(255, 255, 255, 0.92);
            border-color: var(--border);
            border-radius: 8px;
            box-shadow: var(--shadow-soft);
        }

        [data-testid="stSelectbox"] label p,
        [data-testid="stSlider"] label p {
            color: var(--primary-dark);
            font-weight: 760;
            letter-spacing: 0.02em;
        }

        [data-testid="stSlider"] [data-baseweb="slider"] div {
            accent-color: var(--primary);
        }

        [data-testid="stSlider"] [role="slider"] {
            background-color: var(--primary) !important;
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 3px rgba(11, 114, 133, 0.16) !important;
        }

        [data-testid="stSlider"] [data-baseweb="slider"] div[style*="background"] {
            background-color: var(--primary) !important;
        }

        [data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem 1rem 0.95rem;
            box-shadow: var(--shadow-soft);
            position: relative;
            overflow: hidden;
            transform-origin: center;
            transition: transform 220ms cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 220ms ease, border-color 220ms ease;
        }

        [data-testid="stMetric"]::before {
            background: linear-gradient(180deg, var(--primary), rgba(54, 79, 199, 0.76));
            content: "";
            inset: 0 auto 0 0;
            position: absolute;
            width: 4px;
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
            overflow: visible;
            text-overflow: clip;
            white-space: normal;
        }

        [data-testid="stMetric"]:hover {
            border-color: rgba(11, 114, 133, 0.34);
            box-shadow: var(--shadow-lift);
            transform: translateY(-5px) scale(1.035);
        }

        [data-testid="stMetricDelta"] {
            border-radius: 999px;
            display: inline-flex;
            padding: 0.14rem 0.5rem;
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

        [data-testid="stDataFrame"],
        [data-testid="stTable"],
        [data-testid="stJson"],
        [data-testid="stCodeBlock"] {
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(246, 251, 255, 0.96));
            border: 1px solid rgba(188, 205, 216, 0.88);
            box-shadow: 0 16px 40px rgba(15, 23, 42, 0.10);
            overflow: hidden;
        }

        [data-testid="stDataFrame"] [role="columnheader"],
        [data-testid="stDataFrame"] thead tr th,
        [data-testid="stTable"] thead tr th {
            background: #eef7f9 !important;
            color: var(--primary-dark) !important;
            font-weight: 780 !important;
        }

        [data-testid="stDataFrame"] [role="gridcell"],
        [data-testid="stTable"] tbody tr td {
            color: var(--text) !important;
            border-color: rgba(219, 228, 234, 0.74) !important;
        }

        [data-testid="stDataFrame"] div,
        [data-testid="stTable"] div {
            font-variant-numeric: tabular-nums;
        }

        .proof-table-wrap {
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(246, 251, 255, 0.96));
            border: 1px solid rgba(188, 205, 216, 0.88);
            border-radius: 8px;
            box-shadow: 0 16px 40px rgba(15, 23, 42, 0.10);
            margin: 0.55rem 0 1rem;
            overflow: hidden;
        }

        .proof-table {
            border-collapse: collapse;
            table-layout: fixed;
            width: 100%;
        }

        .proof-table thead th {
            background: #eef7f9;
            color: var(--primary-dark);
            font-size: 0.8rem;
            font-weight: 780;
            letter-spacing: 0.02em;
            padding: 0.72rem 0.78rem;
            text-align: left;
        }

        .proof-table tbody td {
            border-top: 1px solid rgba(219, 228, 234, 0.86);
            color: var(--text);
            font-size: 0.9rem;
            line-height: 1.42;
            overflow-wrap: anywhere;
            padding: 0.68rem 0.78rem;
            vertical-align: top;
        }

        .proof-table tbody tr:nth-child(even) td {
            background: rgba(237, 247, 248, 0.44);
        }

        .proof-table tbody tr:hover td {
            background: rgba(231, 246, 248, 0.86);
        }

        [data-testid="stPlotlyChart"] {
            background:
                linear-gradient(90deg, rgba(11, 114, 133, 0.045) 1px, transparent 1px),
                linear-gradient(180deg, rgba(11, 114, 133, 0.04) 1px, transparent 1px),
                linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(241, 248, 251, 0.98));
            background-size: 34px 34px, 34px 34px, auto;
            border: 1px solid rgba(154, 181, 195, 0.92);
            box-shadow: 0 24px 64px rgba(15, 23, 42, 0.14);
            overflow: hidden;
            padding: 0.65rem;
            position: relative;
        }

        [data-testid="stPlotlyChart"]::before {
            background: linear-gradient(90deg, #0b7285, #364fc7 44%, rgba(54, 79, 199, 0.08));
            content: "";
            height: 5px;
            inset: 0 0 auto;
            position: absolute;
            z-index: 1;
        }

        [data-testid="stPlotlyChart"]::after {
            background: radial-gradient(circle, rgba(54, 79, 199, 0.09), transparent 58%);
            content: "";
            height: 170px;
            pointer-events: none;
            position: absolute;
            right: -72px;
            top: -82px;
            width: 240px;
        }

        [data-testid="stPlotlyChart"] .js-plotly-plot .plotly .hoverlayer .hovertext path {
            fill: #ffffff !important;
            stroke: #73cbd7 !important;
            stroke-width: 1.4px !important;
            filter: drop-shadow(0 16px 26px rgba(15, 23, 42, 0.18));
        }

        [data-testid="stPlotlyChart"] .js-plotly-plot .plotly .hoverlayer .hovertext text {
            fill: var(--text) !important;
            font-family: Inter, Segoe UI, Arial, sans-serif !important;
        }

        [data-testid="stAlert"] {
            border-radius: 8px;
            border: 1px solid rgba(15, 23, 42, 0.08);
        }

        [data-testid="stButton"] button,
        [data-testid="baseButton-secondary"],
        [data-testid="baseButton-primary"] {
            border-radius: 8px !important;
            border-color: var(--border) !important;
            box-shadow: var(--shadow-soft) !important;
        }

        [data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, var(--primary), var(--accent)) !important;
            color: #ffffff !important;
        }

        .hero-panel {
            background:
                radial-gradient(circle at 76% 20%, rgba(45, 212, 191, 0.36), transparent 250px),
                radial-gradient(circle at 92% 84%, rgba(79, 70, 229, 0.28), transparent 300px),
                linear-gradient(135deg, rgba(9, 20, 38, 0.99), rgba(7, 82, 96, 0.98) 52%, rgba(40, 57, 169, 0.92)),
                #0f172a;
            border: 1px solid rgba(255, 255, 255, 0.16);
            border-radius: 8px;
            box-shadow: 0 34px 90px rgba(15, 23, 42, 0.28);
            margin-bottom: 1.55rem;
            min-height: 350px;
            overflow: hidden;
            padding: clamp(1.5rem, 5vw, 3.25rem);
            position: relative;
        }

        .hero-panel::before {
            background:
                radial-gradient(circle at center, transparent 0 28px, rgba(178, 242, 255, 0.28) 29px 31px, transparent 32px 54px, rgba(178, 242, 255, 0.18) 55px 57px, transparent 58px),
                linear-gradient(135deg, rgba(255, 255, 255, 0.16), rgba(255, 255, 255, 0.03));
            border: 1px solid rgba(255, 255, 255, 0.16);
            border-radius: 8px;
            content: "";
            height: 230px;
            opacity: 0.62;
            position: absolute;
            right: clamp(-5rem, 2vw, 1.6rem);
            top: 48px;
            transform: rotate(-8deg);
            width: 380px;
        }

        .hero-panel::after {
            background:
                linear-gradient(90deg, rgba(255,255,255,0.13) 1px, transparent 1px),
                linear-gradient(180deg, rgba(255,255,255,0.11) 1px, transparent 1px);
            background-size: 38px 38px;
            content: "";
            inset: 0;
            opacity: 0.30;
            pointer-events: none;
            position: absolute;
        }

        .hero-eyebrow {
            color: #b2f2ff;
            font-weight: 750;
            font-size: 0.82rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.45rem;
        }

        .hero-panel h1,
        .hero-panel p,
        .hero-panel .status-row,
        .hero-panel .hero-eyebrow {
            position: relative;
            z-index: 1;
        }

        .hero-panel h1 {
            color: #fffaf2;
            max-width: 780px;
            text-shadow: 0 2px 20px rgba(0, 0, 0, 0.18);
        }

        .hero-copy {
            max-width: 760px;
            color: #dbeafe;
            font-size: 1.12rem;
            margin: 0.75rem 0 0;
        }

        .status-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 1.35rem;
        }

        .status-pill {
            align-items: center;
            background: rgba(255, 255, 255, 0.14);
            border: 1px solid rgba(255, 255, 255, 0.28);
            border-radius: 999px;
            color: #f8fafc;
            display: inline-flex;
            font-size: 0.82rem;
            font-weight: 700;
            min-height: 34px;
            padding: 0.35rem 0.72rem;
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.16);
        }

        .status-pill.secondary {
            background: rgba(237, 242, 255, 0.16);
            border-color: rgba(186, 200, 255, 0.38);
            color: #dbe4ff;
        }

        .status-pill.pending {
            background: rgba(187, 247, 208, 0.12);
            border-color: rgba(187, 247, 208, 0.32);
            color: #d3f9d8;
        }

        .module-heading {
            background:
                linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(238, 247, 249, 0.96));
            border: 1px solid var(--border);
            border-radius: 8px;
            box-shadow: var(--shadow-soft);
            margin: 1rem 0 1.15rem;
            padding: 1.2rem 1.35rem;
            position: relative;
            overflow: hidden;
        }

        .module-heading::after {
            background: linear-gradient(90deg, var(--primary), transparent);
            content: "";
            height: 3px;
            inset: 0 0 auto;
            opacity: 0.76;
            position: absolute;
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
            background:
                linear-gradient(135deg, #ffffff 0%, #f7fbff 100%);
            border: 1px solid var(--border);
            border-radius: 8px;
            box-shadow: var(--shadow-soft);
            padding: 1.15rem;
            position: relative;
            transform-origin: center;
            transition: transform 220ms cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 220ms ease, border-color 220ms ease, background 220ms ease;
        }

        .insight-card::after {
            background: linear-gradient(90deg, rgba(11, 114, 133, 0.16), rgba(54, 79, 199, 0.08));
            content: "";
            height: 3px;
            inset: auto 1rem 0;
            position: absolute;
        }

        .insight-card:hover,
        .metric-explainer:hover,
        .concept-step:hover {
            border-color: rgba(11, 114, 133, 0.34);
            box-shadow: var(--shadow-lift);
            transform: translateY(-5px) scale(1.035);
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
            font-size: 1.68rem;
            font-weight: 820;
            line-height: 1.2;
            margin-top: 0.32rem;
            overflow-wrap: anywhere;
        }

        .insight-note {
            color: var(--muted);
            font-size: 0.9rem;
            margin-top: 0.45rem;
        }

        .metric-explainer-grid {
            display: grid;
            gap: 1rem;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            margin: 0.4rem 0 1rem;
        }

        .metric-explainer {
            background:
                linear-gradient(135deg, #ffffff 0%, #f6fbff 100%);
            border: 1px solid var(--border);
            border-radius: 8px;
            box-shadow: var(--shadow-soft);
            min-height: 160px;
            padding: 1.18rem 1.1rem 1.05rem 1.25rem;
            position: relative;
            overflow: hidden;
            transform-origin: center;
            transition: transform 220ms cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 220ms ease, border-color 220ms ease, background 220ms ease;
        }

        .metric-explainer::before {
            background: linear-gradient(180deg, var(--primary), var(--accent));
            content: "";
            inset: 0 auto 0 0;
            position: absolute;
            width: 4px;
        }

        .metric-explainer::after {
            background: radial-gradient(circle, rgba(11, 114, 133, 0.12), transparent 64%);
            content: "";
            height: 90px;
            position: absolute;
            right: -32px;
            top: -36px;
            width: 120px;
        }

        .metric-explainer-label {
            color: var(--muted);
            font-size: 0.76rem;
            font-weight: 780;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }

        .metric-explainer-value {
            background: linear-gradient(135deg, var(--text), var(--primary-dark));
            -webkit-background-clip: text;
            color: transparent;
            font-size: clamp(1.75rem, 3vw, 2.25rem);
            font-weight: 820;
            line-height: 1.05;
            margin-top: 0.55rem;
            overflow-wrap: anywhere;
        }

        .metric-explainer-help {
            color: var(--muted);
            font-size: 0.86rem;
            line-height: 1.42;
            margin-top: 0.65rem;
        }

        .health-grid {
            display: grid;
            background:
                radial-gradient(circle at 12% 0%, rgba(45, 212, 191, 0.16), transparent 220px),
                linear-gradient(135deg, #071827, #073b4c 48%, #172554);
            border: 1px solid rgba(178, 242, 255, 0.22);
            border-radius: 8px;
            box-shadow: 0 28px 76px rgba(15, 23, 42, 0.22);
            gap: 0.8rem;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            margin: 0.8rem 0 1.25rem;
            padding: 0.9rem;
            position: relative;
            overflow: hidden;
        }

        .health-grid::before {
            background:
                linear-gradient(90deg, rgba(255,255,255,0.08) 1px, transparent 1px),
                linear-gradient(180deg, rgba(255,255,255,0.07) 1px, transparent 1px);
            background-size: 28px 28px;
            content: "";
            inset: 0;
            opacity: 0.46;
            pointer-events: none;
            position: absolute;
        }

        .health-card {
            background: rgba(255, 255, 255, 0.10);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 8px;
            box-shadow: 0 18px 42px rgba(0, 0, 0, 0.14);
            min-height: 145px;
            overflow: hidden;
            padding: 1rem 1rem 0.95rem 1.1rem;
            position: relative;
            z-index: 1;
        }

        .health-card::before {
            content: "";
            inset: 0 auto 0 0;
            position: absolute;
            width: 5px;
        }

        .health-card.good::before {
            background: #51cf66;
        }

        .health-card.watch::before {
            background: #ffd43b;
        }

        .health-card.risk::before {
            background: #ff6b6b;
        }

        .health-card.info::before {
            background: #74c0fc;
        }

        .health-label {
            color: #b2f2ff;
            font-size: 0.74rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .health-status {
            color: #f8fafc;
            font-size: 1.35rem;
            font-weight: 860;
            line-height: 1.18;
            margin-top: 0.48rem;
            text-shadow: 0 14px 28px rgba(0, 0, 0, 0.22);
        }

        .health-detail {
            color: #dbeafe;
            font-size: 0.9rem;
            line-height: 1.42;
            margin-top: 0.58rem;
        }

        .anomaly-card-grid {
            display: grid;
            gap: 0.95rem;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            margin: 0.85rem 0 1.2rem;
        }

        .anomaly-card {
            background:
                radial-gradient(circle at 100% 0%, rgba(54, 79, 199, 0.12), transparent 150px),
                linear-gradient(135deg, #ffffff, #f6fbff);
            border: 1px solid rgba(154, 181, 195, 0.92);
            border-radius: 8px;
            box-shadow: 0 20px 54px rgba(15, 23, 42, 0.13);
            min-height: 250px;
            overflow: hidden;
            padding: 1.05rem 1.05rem 1rem;
            position: relative;
        }

        .anomaly-card::before {
            background: linear-gradient(180deg, #364fc7, #0b7285);
            content: "";
            inset: 0 auto 0 0;
            position: absolute;
            width: 5px;
        }

        .anomaly-kicker {
            color: var(--accent);
            font-size: 0.74rem;
            font-weight: 840;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .anomaly-title {
            color: var(--text);
            font-size: 1.15rem;
            font-weight: 840;
            line-height: 1.22;
            margin-top: 0.35rem;
        }

        .anomaly-body {
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.48;
            margin-top: 0.55rem;
        }

        .anomaly-list {
            list-style: none;
            margin: 0.75rem 0 0;
            padding: 0;
        }

        .anomaly-list li {
            background: rgba(231, 246, 248, 0.76);
            border: 1px solid rgba(123, 199, 209, 0.30);
            border-radius: 8px;
            color: #334155;
            font-size: 0.86rem;
            line-height: 1.38;
            margin-top: 0.42rem;
            padding: 0.48rem 0.58rem;
        }

        .story-panel,
        .takeaway-panel {
            background:
                linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(246, 251, 255, 0.98));
            border: 1px solid var(--border);
            border-radius: 8px;
            box-shadow: var(--shadow-soft);
            margin: 0.95rem 0 1.15rem;
            padding: clamp(1.1rem, 2.8vw, 1.55rem);
            position: relative;
            overflow: hidden;
        }

        .story-panel {
            border-left: 5px solid var(--primary);
        }

        .story-panel::after,
        .takeaway-panel::after {
            background: radial-gradient(circle, rgba(54, 79, 199, 0.08), transparent 64%);
            content: "";
            height: 130px;
            position: absolute;
            right: -54px;
            top: -58px;
            width: 170px;
        }

        .story-kicker,
        .takeaway-kicker {
            color: var(--primary-dark);
            font-size: 0.75rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .story-title,
        .takeaway-title {
            color: var(--text);
            font-size: 1.18rem;
            font-weight: 780;
            line-height: 1.25;
            margin-top: 0.25rem;
        }

        .story-body,
        .takeaway-body {
            color: var(--muted);
            margin-top: 0.45rem;
            position: relative;
            z-index: 1;
        }

        .story-list {
            color: var(--muted);
            margin: 0.65rem 0 0;
            padding-left: 1.1rem;
            position: relative;
            z-index: 1;
        }

        .takeaway-panel {
            background: linear-gradient(180deg, #f7fbff, #ffffff);
            border-color: #c7d7fe;
        }

        .takeaway-panel.success {
            background: linear-gradient(180deg, #ebfbee, #ffffff);
            border-color: #b2f2bb;
        }

        .takeaway-panel.warning {
            background: linear-gradient(180deg, #fff9e8, #ffffff);
            border-color: #f5d78a;
        }

        .concept-flow {
            display: grid;
            gap: 0.8rem;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            margin: 0.75rem 0 1.15rem;
        }

        .concept-step {
            background:
                linear-gradient(135deg, #ffffff 0%, #f6fbff 100%);
            border: 1px solid var(--border);
            border-radius: 8px;
            box-shadow: var(--shadow-soft);
            padding: 1.15rem;
            position: relative;
            overflow: hidden;
            transform-origin: center;
            transition: transform 220ms cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 220ms ease, border-color 220ms ease, background 220ms ease;
        }

        .concept-step::after {
            background: linear-gradient(180deg, rgba(11, 114, 133, 0.08), transparent);
            content: "";
            inset: 0;
            pointer-events: none;
            position: absolute;
        }

        .concept-number {
            align-items: center;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            border-radius: 999px;
            color: #ffffff;
            display: inline-flex;
            font-size: 0.78rem;
            font-weight: 800;
            height: 30px;
            justify-content: center;
            width: 30px;
            position: relative;
            z-index: 1;
        }

        .concept-title {
            color: var(--text);
            font-size: 1rem;
            font-weight: 780;
            margin-top: 0.65rem;
            position: relative;
            z-index: 1;
        }

        .concept-body {
            color: var(--muted);
            font-size: 0.92rem;
            margin-top: 0.35rem;
            position: relative;
            z-index: 1;
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
            .insight-card,
            .metric-explainer,
            [data-testid="stMetric"],
            .story-panel,
            .takeaway-panel,
            .concept-step {
                box-shadow: none;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            .insight-card,
            .metric-explainer,
            [data-testid="stMetric"],
            .concept-step {
                transition: none;
            }

            .insight-card:hover,
            .metric-explainer:hover,
            [data-testid="stMetric"]:hover,
            .concept-step:hover {
                transform: none;
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
            <div class="hero-eyebrow">ProofLab Bitcoin</div>
            <h1>Una visita guiada por la prueba de trabajo de Bitcoin</h1>
            <p class="hero-copy">
                Primero se aclaran las piezas basicas de Bitcoin; despues se pasa a datos reales,
                verificacion local del hash, ajuste de dificultad y deteccion de intervalos raros.
            </p>
            <div class="status-row">
                <span class="status-pill">Datos reales</span>
                <span class="status-pill">Hash verificado</span>
                <span class="status-pill">Dificultad explicada</span>
                <span class="status-pill secondary">IA interpretable</span>
                <span class="status-pill pending">Lectura guiada</span>
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


def metric_explainer_grid(items: list[tuple[str, str, str]]) -> None:
    cards = "".join(
        (
            '<article class="metric-explainer">'
            f'<div class="metric-explainer-label">{escape(label)}</div>'
            f'<div class="metric-explainer-value">{escape(value)}</div>'
            f'<div class="metric-explainer-help">{escape(help_text)}</div>'
            "</article>"
        )
        for label, value, help_text in items
    )
    st.markdown(f'<div class="metric-explainer-grid">{cards}</div>', unsafe_allow_html=True)


def health_grid(items: list[tuple[str, str, str, str]]) -> None:
    cards = "".join(
        (
            f'<article class="health-card {escape(tone)}">'
            f'<div class="health-label">{escape(label)}</div>'
            f'<div class="health-status">{escape(status)}</div>'
            f'<div class="health-detail">{escape(detail)}</div>'
            "</article>"
        )
        for label, status, detail, tone in items
    )
    st.markdown(f'<div class="health-grid">{cards}</div>', unsafe_allow_html=True)


def anomaly_card_grid(items: list[tuple[str, str, str, list[str]]]) -> None:
    cards = "".join(
        (
            '<article class="anomaly-card">'
            f'<div class="anomaly-kicker">{escape(kicker)}</div>'
            f'<div class="anomaly-title">{escape(title)}</div>'
            f'<div class="anomaly-body">{escape(body)}</div>'
            '<ul class="anomaly-list">'
            + "".join(f"<li>{escape(reason)}</li>" for reason in reasons)
            + "</ul>"
            "</article>"
        )
        for kicker, title, body, reasons in items
    )
    st.markdown(f'<div class="anomaly-card-grid">{cards}</div>', unsafe_allow_html=True)


def story_panel(kicker: str, title: str, body: str, bullets: list[str] | None = None) -> None:
    bullet_html = ""
    if bullets:
        bullet_html = "<ul class=\"story-list\">" + "".join(f"<li>{escape(item)}</li>" for item in bullets) + "</ul>"
    st.markdown(
        (
            '<section class="story-panel">'
            f'<div class="story-kicker">{escape(kicker)}</div>'
            f'<div class="story-title">{escape(title)}</div>'
            f'<div class="story-body">{escape(body)}</div>'
            f"{bullet_html}"
            "</section>"
        ),
        unsafe_allow_html=True,
    )


def takeaway(title: str, body: str, *, tone: str = "default") -> None:
    safe_tone = tone if tone in {"default", "success", "warning"} else "default"
    st.markdown(
        (
            f'<section class="takeaway-panel {safe_tone}">'
            '<div class="takeaway-kicker">Lectura rapida</div>'
            f'<div class="takeaway-title">{escape(title)}</div>'
            f'<div class="takeaway-body">{escape(body)}</div>'
            "</section>"
        ),
        unsafe_allow_html=True,
    )


def concept_flow(items: list[tuple[str, str]]) -> None:
    cards = "".join(
        (
            '<article class="concept-step">'
            f'<div class="concept-number">{index}</div>'
            f'<div class="concept-title">{escape(title)}</div>'
            f'<div class="concept-body">{escape(body)}</div>'
            "</article>"
        )
        for index, (title, body) in enumerate(items, start=1)
    )
    st.markdown(f'<div class="concept-flow">{cards}</div>', unsafe_allow_html=True)


def styled_table(frame: object) -> None:
    table_html = frame.to_html(index=False, escape=True, classes="proof-table", border=0)  # type: ignore[attr-defined]
    st.markdown(f'<div class="proof-table-wrap">{table_html}</div>', unsafe_allow_html=True)


def style_chart(fig: go.Figure, *, height: int | None = None) -> go.Figure:
    fig.update_layout(
        colorway=COLORWAY,
        dragmode=False,
        font={"family": "Inter, Segoe UI, Arial, sans-serif", "color": "#0f172a"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248,251,253,0.92)",
        margin={"l": 46, "r": 26, "t": 78, "b": 52},
        title={
            "font": {"size": 17, "color": "#172033", "family": "Inter, Segoe UI, Arial, sans-serif"},
            "x": 0.02,
            "xanchor": "left",
            "y": 0.96,
            "yanchor": "top",
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.08,
            "xanchor": "right",
            "x": 1,
            "bgcolor": "rgba(255,255,255,0.74)",
            "bordercolor": "rgba(188,205,216,0.68)",
            "borderwidth": 1,
            "font": {"size": 12, "color": "#334155"},
            "itemsizing": "constant",
        },
        hovermode="closest",
        hoverlabel={
            "align": "left",
            "bgcolor": "#ffffff",
            "font": {"family": "Inter, Segoe UI, Arial, sans-serif", "size": 13, "color": "#172033"},
            "bordercolor": "#364fc7",
            "namelength": -1,
        },
        separators=".,",
    )
    fig.update_traces(marker_line_color="rgba(255,255,255,0.88)", marker_line_width=1.1, selector={"type": "bar"})
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(11, 114, 133, 0.10)",
        linecolor="rgba(188, 205, 216, 0.78)",
        tickfont={"color": "#64748b", "size": 12},
        title_font={"color": "#596579", "size": 13},
        zeroline=False,
        fixedrange=True,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(11, 114, 133, 0.10)",
        linecolor="rgba(188, 205, 216, 0.78)",
        tickfont={"color": "#64748b", "size": 12},
        title_font={"color": "#596579", "size": 13},
        zeroline=False,
        fixedrange=True,
    )
    if height is not None:
        fig.update_layout(height=height)
    return fig
