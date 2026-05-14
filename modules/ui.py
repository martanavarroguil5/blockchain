from __future__ import annotations

from html import escape

import plotly.graph_objects as go
import streamlit as st


COLORWAY = ["#087F8C", "#2563EB", "#4F46E5", "#0EA5E9", "#1D4ED8", "#0F766E"]


def apply_app_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #eef4f1;
            --surface: #ffffff;
            --surface-soft: #f3f8f6;
            --surface-strong: #f9fcfb;
            --ink: #101724;
            --text: #182235;
            --muted: #5d687b;
            --border: #d6e0df;
            --border-strong: #b6c6c5;
            --primary: #087f8c;
            --primary-dark: #07545c;
            --primary-soft: #e5f7f6;
            --accent: #2563eb;
            --accent-soft: #e0ecff;
            --accent-2: #4f46e5;
            --accent-2-soft: #eef2ff;
            --success: #2563eb;
            --warning: #1d4ed8;
            --radius: 8px;
            --shadow: 0 32px 78px rgba(15, 23, 42, 0.18);
            --shadow-lift: 0 26px 58px rgba(8, 127, 140, 0.18), 0 12px 30px rgba(15, 23, 42, 0.12);
            --shadow-soft: 0 16px 38px rgba(15, 23, 42, 0.09);
            --shadow-hairline: inset 0 1px 0 rgba(255, 255, 255, 0.78);
        }

        .stApp {
            background:
                linear-gradient(90deg, rgba(8, 127, 140, 0.050) 1px, transparent 1px),
                linear-gradient(180deg, rgba(37, 99, 235, 0.045) 1px, transparent 1px),
                linear-gradient(135deg, rgba(224, 236, 255, 0.74) 0%, rgba(232, 247, 247, 0.82) 38%, rgba(236, 242, 255, 0.88) 100%),
                linear-gradient(180deg, #f8fbff 0, #eef4f8 100%),
                var(--bg);
            background-size: 34px 34px, 34px 34px, auto, auto;
            color: var(--text);
        }

        .block-container {
            max-width: 1320px;
            padding-top: 1.35rem;
            padding-bottom: 4.5rem;
        }

        .stApp * {
            text-rendering: optimizeLegibility;
        }

        .stApp a {
            color: var(--primary-dark);
            text-decoration-thickness: 0.08em;
            text-underline-offset: 0.16em;
        }

        [data-testid="stSidebar"] {
            background:
                linear-gradient(90deg, rgba(255, 255, 255, 0.055) 1px, transparent 1px),
                linear-gradient(180deg, rgba(255, 255, 255, 0.050) 1px, transparent 1px),
                linear-gradient(180deg, #0b1220 0%, #102133 52%, #0f3b61 100%);
            background-size: 22px 22px, 22px 22px, auto;
            border-right: 1px solid rgba(255, 255, 255, 0.10);
            box-shadow: 18px 0 48px rgba(15, 23, 42, 0.20);
        }

        [data-testid="stSidebar"] * {
            color: #e5eef8;
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.15rem;
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            letter-spacing: 0;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] li {
            color: #cbd5e1;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p strong {
            color: #f8fafc !important;
            opacity: 1 !important;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p:has(strong) {
            color: #f8fafc !important;
            opacity: 1 !important;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #f8fafc !important;
        }

        [data-testid="stSidebar"] [data-testid="stAlert"] {
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(178, 242, 255, 0.20);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
        }

        [data-testid="stSidebar"] [data-testid="stAlert"] p {
            color: #dbeafe !important;
        }

        [data-testid="stSidebarNav"] {
            padding-top: 0;
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

        div[data-testid="stCaptionContainer"],
        div[data-testid="stCaptionContainer"] p {
            color: #697589;
            font-size: 0.86rem;
        }

        input[type="radio"],
        input[type="checkbox"],
        input[type="range"] {
            accent-color: var(--primary);
        }

        [data-testid="stElementContainer"]:has([data-testid="stRadio"]) {
            width: 100% !important;
        }

        [data-testid="stRadio"],
        [data-testid="stRadio"] > div,
        [data-testid="stRadio"] > div:nth-child(2) {
            width: 100% !important;
        }

        [data-testid="stRadio"] [role="radiogroup"] {
            background: rgba(255, 255, 255, 0.80);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(182, 198, 197, 0.82);
            border-radius: var(--radius);
            box-shadow: var(--shadow-soft), var(--shadow-hairline);
            display: grid !important;
            gap: 0.5rem;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            padding: 0.5rem;
            width: 100% !important;
        }

        [data-testid="stRadio"] label {
            background: transparent;
            border: 1px solid transparent;
            border-radius: var(--radius);
            min-height: 46px;
            padding: 0.26rem 0.92rem;
            transition: background-color 180ms ease, border-color 180ms ease, box-shadow 180ms ease, transform 180ms ease;
            justify-content: center;
            width: 100%;
        }

        [data-testid="stRadio"] label:hover {
            background: rgba(229, 247, 246, 0.68);
            border-color: rgba(8, 127, 140, 0.18);
            transform: translateY(-1px);
        }

        [data-testid="stRadio"] label [data-testid="stMarkdownContainer"],
        [data-testid="stRadio"] label [data-testid="stMarkdownContainer"] p {
            text-align: center;
            width: 100%;
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
            background:
                linear-gradient(135deg, rgba(229, 247, 246, 0.98), rgba(238, 242, 255, 0.96));
            border-color: rgba(8, 127, 140, 0.42);
            box-shadow: 0 12px 24px rgba(8, 127, 140, 0.16), inset 0 0 0 1px rgba(8, 127, 140, 0.22);
        }

        [data-testid="stRadio"] label:has(input:checked) p {
            color: var(--primary-dark);
            font-weight: 760;
        }

        [data-testid="stSelectbox"] [data-baseweb="select"] > div {
            background: rgba(255, 255, 255, 0.92);
            border-color: var(--border);
            border-radius: var(--radius);
            box-shadow: var(--shadow-soft), var(--shadow-hairline);
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
            background:
                linear-gradient(135deg, rgba(255, 255, 255, 0.99), rgba(249, 252, 251, 0.98));
            border: 1px solid rgba(214, 224, 223, 0.94);
            border-radius: var(--radius);
            padding: 1rem 1rem 0.95rem;
            box-shadow: var(--shadow-soft), var(--shadow-hairline);
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
            transform: translateY(-3px) scale(1.012);
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
            border-radius: var(--radius) var(--radius) 0 0;
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
            border-radius: var(--radius);
        }

        [data-testid="stDataFrame"],
        [data-testid="stTable"],
        [data-testid="stJson"],
        [data-testid="stCodeBlock"] {
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.99), rgba(249, 252, 251, 0.98));
            border: 1px solid rgba(182, 198, 197, 0.88);
            box-shadow: var(--shadow-soft), var(--shadow-hairline);
            overflow: hidden;
        }

        [data-testid="stDataFrame"] [role="columnheader"],
        [data-testid="stDataFrame"] thead tr th,
        [data-testid="stTable"] thead tr th {
            background: #e8f5f4 !important;
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
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.99), rgba(249, 252, 251, 0.98));
            border: 1px solid rgba(182, 198, 197, 0.88);
            border-radius: var(--radius);
            box-shadow: var(--shadow-soft), var(--shadow-hairline);
            margin: 0.55rem 0 1rem;
            overflow: hidden;
        }

        .proof-table {
            border-collapse: collapse;
            table-layout: fixed;
            width: 100%;
        }

        .proof-table thead th {
            background: #e8f5f4;
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
            background: rgba(243, 248, 246, 0.66);
        }

        .proof-table tbody tr:hover td {
            background: rgba(229, 247, 246, 0.82);
        }

        [data-testid="stPlotlyChart"] {
            background:
                linear-gradient(90deg, rgba(8, 127, 140, 0.045) 1px, transparent 1px),
                linear-gradient(180deg, rgba(79, 70, 229, 0.040) 1px, transparent 1px),
                linear-gradient(180deg, rgba(255, 255, 255, 0.99), rgba(246, 250, 249, 0.99));
            background-size: 34px 34px, 34px 34px, auto;
            border: 1px solid rgba(154, 181, 181, 0.88);
            box-shadow: 0 22px 58px rgba(15, 23, 42, 0.12), var(--shadow-hairline);
            overflow: hidden;
            padding: 0.65rem;
            position: relative;
        }

        [data-testid="stPlotlyChart"]::before {
            background: linear-gradient(90deg, var(--primary), var(--accent) 48%, var(--accent-2));
            content: "";
            height: 4px;
            inset: 0 0 auto;
            position: absolute;
            z-index: 1;
        }

        [data-testid="stPlotlyChart"]::after {
            content: none;
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
            border-radius: var(--radius);
            border: 1px solid rgba(15, 23, 42, 0.08);
            box-shadow: var(--shadow-hairline);
        }

        [data-testid="stButton"] button,
        [data-testid="baseButton-secondary"],
        [data-testid="baseButton-primary"] {
            border-radius: var(--radius) !important;
            border-color: var(--border) !important;
            box-shadow: var(--shadow-soft), var(--shadow-hairline) !important;
            min-height: 44px;
            transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
        }

        [data-testid="stButton"] button:hover,
        [data-testid="baseButton-secondary"]:hover,
        [data-testid="baseButton-primary"]:hover {
            border-color: rgba(8, 127, 140, 0.38) !important;
            transform: translateY(-1px);
        }

        [data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, var(--primary), var(--accent)) !important;
            color: #ffffff !important;
        }

        .hero-panel {
            background:
                linear-gradient(90deg, rgba(255,255,255,0.10) 1px, transparent 1px),
                linear-gradient(180deg, rgba(255,255,255,0.08) 1px, transparent 1px),
                linear-gradient(135deg, rgba(9, 20, 38, 0.99), rgba(7, 84, 92, 0.98) 50%, rgba(55, 47, 151, 0.94)),
                #0f172a;
            background-size: 36px 36px, 36px 36px, auto, auto;
            border: 1px solid rgba(255, 255, 255, 0.16);
            border-radius: var(--radius);
            box-shadow: 0 34px 90px rgba(15, 23, 42, 0.26), inset 0 1px 0 rgba(255, 255, 255, 0.12);
            margin-bottom: 1.55rem;
            min-height: 350px;
            overflow: hidden;
            padding: clamp(1.5rem, 5vw, 3.25rem);
            position: relative;
        }

        .hero-panel::before {
            background:
                linear-gradient(90deg, rgba(178, 242, 255, 0.20) 1px, transparent 1px),
                linear-gradient(180deg, rgba(178, 242, 255, 0.16) 1px, transparent 1px),
                linear-gradient(135deg, rgba(255, 255, 255, 0.17), rgba(255, 255, 255, 0.04));
            background-size: 22px 22px, 22px 22px, auto;
            border: 1px solid rgba(255, 255, 255, 0.16);
            border-radius: var(--radius);
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
                linear-gradient(90deg, transparent, rgba(255, 247, 230, 0.18), transparent),
                linear-gradient(180deg, rgba(255,255,255,0.08), transparent 45%);
            background-size: auto;
            content: "";
            inset: 0;
            opacity: 0.70;
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
            color: #deebf4;
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
            background: rgba(255, 255, 255, 0.13);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.28);
            border-radius: 999px;
            color: #f8fafc;
            display: inline-flex;
            font-size: 0.82rem;
            font-weight: 700;
            min-height: 34px;
            padding: 0.35rem 0.72rem;
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.08);
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
                linear-gradient(135deg, rgba(255, 255, 255, 0.99), rgba(243, 248, 246, 0.98));
            border: 1px solid rgba(214, 224, 223, 0.92);
            border-radius: var(--radius);
            box-shadow: var(--shadow-soft), var(--shadow-hairline);
            margin: 1rem 0 1.15rem;
            padding: 1.2rem 1.35rem;
            position: relative;
            overflow: hidden;
        }

        .module-heading::after {
            background: linear-gradient(90deg, var(--primary), var(--accent), var(--accent-2), transparent);
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
            gap: 0.9rem;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            margin: 0.7rem 0 1.15rem;
        }

        .insight-card {
            background:
                linear-gradient(135deg, rgba(255, 255, 255, 0.99) 0%, rgba(249, 252, 251, 0.98) 100%);
            border: 1px solid rgba(214, 224, 223, 0.94);
            border-radius: var(--radius);
            box-shadow: var(--shadow-soft), var(--shadow-hairline);
            padding: 1.15rem;
            position: relative;
            overflow: hidden;
            transform-origin: center;
            transition: transform 220ms cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 220ms ease, border-color 220ms ease, background 220ms ease;
        }

        .insight-card::after {
            background: linear-gradient(90deg, rgba(8, 127, 140, 0.26), rgba(37, 99, 235, 0.16), rgba(79, 70, 229, 0.18));
            content: "";
            height: 4px;
            inset: auto 0 0;
            position: absolute;
        }

        .insight-card:hover,
        .metric-explainer:hover,
        .concept-step:hover {
            border-color: rgba(11, 114, 133, 0.34);
            box-shadow: var(--shadow-lift);
            transform: translateY(-3px) scale(1.012);
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
                linear-gradient(135deg, rgba(255, 255, 255, 0.99) 0%, rgba(249, 252, 251, 0.98) 100%);
            border: 1px solid rgba(214, 224, 223, 0.94);
            border-radius: var(--radius);
            box-shadow: var(--shadow-soft), var(--shadow-hairline);
            min-height: 160px;
            padding: 1.18rem 1.1rem 1.05rem 1.25rem;
            position: relative;
            overflow: hidden;
            transform-origin: center;
            transition: transform 220ms cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 220ms ease, border-color 220ms ease, background 220ms ease;
        }

        .metric-explainer::before {
            background: linear-gradient(180deg, var(--primary), var(--accent), var(--accent-2));
            content: "";
            inset: 0 auto 0 0;
            position: absolute;
            width: 4px;
        }

        .metric-explainer::after {
            background:
                linear-gradient(90deg, rgba(8, 127, 140, 0.10) 1px, transparent 1px),
                linear-gradient(180deg, rgba(37, 99, 235, 0.09) 1px, transparent 1px);
            background-size: 15px 15px;
            content: "";
            height: 90px;
            opacity: 0.46;
            position: absolute;
            right: -24px;
            top: -28px;
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
                linear-gradient(90deg, rgba(255,255,255,0.075) 1px, transparent 1px),
                linear-gradient(180deg, rgba(255,255,255,0.060) 1px, transparent 1px),
                linear-gradient(135deg, #071827, #073b4c 48%, #172554);
            background-size: 28px 28px, 28px 28px, auto;
            border: 1px solid rgba(178, 242, 255, 0.22);
            border-radius: var(--radius);
            box-shadow: 0 28px 76px rgba(15, 23, 42, 0.22);
            gap: 0.8rem;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            margin: 0.8rem 0 1.25rem;
            padding: 0.9rem;
            position: relative;
            overflow: hidden;
        }

        .health-grid::before {
            content: none;
        }

        .health-card {
            background: rgba(255, 255, 255, 0.10);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: var(--radius);
            box-shadow: 0 18px 42px rgba(0, 0, 0, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.08);
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
                linear-gradient(90deg, rgba(8, 127, 140, 0.052) 1px, transparent 1px),
                linear-gradient(180deg, rgba(79, 70, 229, 0.045) 1px, transparent 1px),
                linear-gradient(135deg, #ffffff, #f8fbfa);
            background-size: 26px 26px, 26px 26px, auto;
            border: 1px solid rgba(154, 181, 181, 0.88);
            border-radius: var(--radius);
            box-shadow: 0 20px 54px rgba(15, 23, 42, 0.12), var(--shadow-hairline);
            min-height: 250px;
            overflow: hidden;
            padding: 1.05rem 1.05rem 1rem;
            position: relative;
            transition: transform 220ms ease, box-shadow 220ms ease, border-color 220ms ease;
        }

        .anomaly-card::before {
            background: linear-gradient(180deg, var(--accent), var(--primary), var(--accent-2));
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
            background: rgba(229, 247, 246, 0.76);
            border: 1px solid rgba(123, 199, 209, 0.34);
            border-radius: var(--radius);
            color: #334155;
            font-size: 0.86rem;
            line-height: 1.38;
            margin-top: 0.42rem;
            padding: 0.48rem 0.58rem;
        }

        .story-panel,
        .takeaway-panel {
            background:
                linear-gradient(135deg, rgba(255, 255, 255, 0.99), rgba(249, 252, 251, 0.98));
            border: 1px solid rgba(214, 224, 223, 0.94);
            border-radius: var(--radius);
            box-shadow: var(--shadow-soft), var(--shadow-hairline);
            margin: 0.95rem 0 1.15rem;
            padding: clamp(1.1rem, 2.8vw, 1.55rem);
            position: relative;
            overflow: hidden;
            transition: transform 220ms ease, box-shadow 220ms ease, border-color 220ms ease;
        }

        .story-panel {
            border-left: 5px solid var(--primary);
        }

        .story-panel::after,
        .takeaway-panel::after {
            background:
                linear-gradient(90deg, rgba(8, 127, 140, 0.085) 1px, transparent 1px),
                linear-gradient(180deg, rgba(79, 70, 229, 0.070) 1px, transparent 1px);
            background-size: 16px 16px;
            content: "";
            height: 130px;
            opacity: 0.50;
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
            background: linear-gradient(180deg, #f3f7ff, #ffffff);
            border-color: #c7d7fe;
        }

        .takeaway-panel.success {
            background: linear-gradient(180deg, #edf7ff, #ffffff);
            border-color: #b8d7ff;
        }

        .takeaway-panel.warning {
            background: linear-gradient(180deg, #e8f2ff, #ffffff);
            border-color: #bfd3ff;
        }

        .concept-flow {
            display: grid;
            gap: 0.8rem;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            margin: 0.75rem 0 1.15rem;
        }

        .concept-step {
            background:
                linear-gradient(135deg, rgba(255, 255, 255, 0.99) 0%, rgba(249, 252, 251, 0.98) 100%);
            border: 1px solid rgba(214, 224, 223, 0.94);
            border-radius: var(--radius);
            box-shadow: var(--shadow-soft), var(--shadow-hairline);
            padding: 1.15rem;
            position: relative;
            overflow: hidden;
            transform-origin: center;
            transition: transform 220ms cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 220ms ease, border-color 220ms ease, background 220ms ease;
        }

        .concept-step::after {
            background:
                linear-gradient(180deg, rgba(8, 127, 140, 0.07), transparent 54%),
                linear-gradient(90deg, rgba(8, 127, 140, 0.075) 1px, transparent 1px);
            background-size: auto, 18px 18px;
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
            box-shadow: 0 10px 20px rgba(8, 127, 140, 0.22);
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

        [data-testid="stCodeBlock"] pre {
            background: #0f172a !important;
            border: 1px solid rgba(255, 255, 255, 0.10);
        }

        [data-testid="stCodeBlock"] code {
            color: #dbeafe !important;
            font-variant-ligatures: none;
        }

        @media (max-width: 760px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            [data-testid="stRadio"] [role="radiogroup"] {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            [data-testid="stRadio"] label {
                min-height: 44px;
                padding-left: 0.55rem;
                padding-right: 0.55rem;
            }

            .hero-panel {
                min-height: 310px;
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
            <h1>A guided tour of Bitcoin Proof of Work</h1>
            <p class="hero-copy">
                First, the basic pieces of Bitcoin are clarified; then the app moves into real data,
                local hash verification, difficulty adjustment, and detection of unusual intervals.
            </p>
            <div class="status-row">
                <span class="status-pill">Real data</span>
                <span class="status-pill">Verified hash</span>
                <span class="status-pill">Difficulty explained</span>
                <span class="status-pill secondary">Interpretable AI</span>
                <span class="status-pill pending">Guided reading</span>
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
            '<div class="takeaway-kicker">Quick reading</div>'
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
        font={"family": "Inter, Segoe UI, Arial, sans-serif", "color": "#182235"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(249,252,251,0.94)",
        margin={"l": 46, "r": 26, "t": 78, "b": 52},
        title={
            "font": {"size": 17, "color": "#182235", "family": "Inter, Segoe UI, Arial, sans-serif"},
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
            "bordercolor": "rgba(182,198,197,0.72)",
            "borderwidth": 1,
            "font": {"size": 12, "color": "#334155"},
            "itemsizing": "constant",
        },
        hovermode="closest",
        hoverlabel={
            "align": "left",
            "bgcolor": "#ffffff",
            "font": {"family": "Inter, Segoe UI, Arial, sans-serif", "size": 13, "color": "#182235"},
            "bordercolor": "#4F46E5",
            "namelength": -1,
        },
        separators=".,",
    )
    fig.update_traces(marker_line_color="rgba(255,255,255,0.88)", marker_line_width=1.1, selector={"type": "bar"})
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(8, 127, 140, 0.10)",
        linecolor="rgba(182, 198, 197, 0.78)",
        tickfont={"color": "#64748b", "size": 12},
        title_font={"color": "#596579", "size": 13},
        zeroline=False,
        fixedrange=True,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(8, 127, 140, 0.10)",
        linecolor="rgba(182, 198, 197, 0.78)",
        tickfont={"color": "#64748b", "size": 12},
        title_font={"color": "#596579", "size": 13},
        zeroline=False,
        fixedrange=True,
    )
    if height is not None:
        fig.update_layout(height=height)
    return fig
