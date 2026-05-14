from __future__ import annotations

import streamlit as st
import pandas as pd

from modules.m1_pow_monitor import render_m1
from modules.m2_block_header import render_m2
from modules.m3_difficulty_history import render_m3
from modules.m4_ai_anomaly import render_m4
from modules.ui import apply_app_theme, concept_flow, hero, insight_grid, story_panel, styled_table, takeaway


st.set_page_config(
    page_title="ProofLab Bitcoin",
    page_icon="C",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_app_theme()
hero()

with st.sidebar:
    st.header("ProofLab Bitcoin")
    st.markdown("**Author:** Marta Navarro")
    st.markdown("**Topic:** Proof of Work in Bitcoin")
    st.divider()
    st.markdown("**Reading path**")
    st.markdown("1. Live network")
    st.markdown("2. Inside a block")
    st.markdown("3. Difficulty")
    st.markdown("4. AI anomalies")
    st.info("Each section uses real data and explains how to read what you are seeing.")

selected_page = st.radio(
    "Section",
    [
        "Map",
        "Live network",
        "Inside a block",
        "Difficulty",
        "AI anomalies",
    ],
    horizontal=True,
    label_visibility="collapsed",
)

if selected_page == "Map":
    st.subheader("Reading map")
    story_panel(
        "Core concepts",
        "Before looking at data, it helps to know the basic pieces of Bitcoin.",
        "Bitcoin is a public ledger of transactions. Transactions are grouped into blocks, "
        "each block is linked to the previous one, and together they form the blockchain. To add a block, "
        "miners try many hashes. The rule they must satisfy is very specific: the block hash, interpreted as a number, "
        "must be lower than a target number. Difficulty is not that target itself; it is a way to express how much the rule has been hardened: "
        "if it reads 134 T, finding a valid hash is about 134 trillion times harder than at the base level.",
        [
            "Block: a package of transactions accepted as a new page of the ledger.",
            "Chain: a sequence of linked blocks; each block cryptographically depends on the previous one.",
            "Hash: the numeric fingerprint of a block; if the block changes, the hash changes.",
            "Miners: computers that try hashes to propose the next block.",
            "Difficulty: a scale that tightens the hash target; the higher it is, the fewer hashes satisfy the rule.",
            "Height: the position of a block inside the chain.",
        ],
    )
    story_panel(
        "Main idea",
        "The app explains how Bitcoin decides that a block is valid.",
        "The idea is to follow the full path: first see what is happening on the network now, "
        "then look inside a real block, verify its hash, and understand why difficulty changes over time. "
        "At the end, recent data is used to detect block intervals that fall outside the usual pattern.",
        [
            "Live network: shows the latest block, difficulty, hash rate, and transactions.",
            "Inside a block: shows the technical fields of a block and recalculates its hash.",
            "Difficulty: explains how Bitcoin tries to maintain an average rhythm of 10 minutes per block.",
            "AI anomalies: searches for blocks whose arrival time was unusual compared with recent context.",
        ],
    )
    insight_grid(
        [
            ("Real block", "Live data", "The information comes from public Bitcoin explorers."),
            ("Local proof", "SHA-256 x2", "The header hash is recalculated from scratch."),
            ("Expected rhythm", "10 min", "Difficulty tries to keep that average over the long term."),
            ("AI", "Isolation Forest", "The model highlights unusual timing patterns."),
        ]
    )
    st.markdown("#### Walkthrough")
    concept_flow(
        [
            (
                "Observe",
                "Shows the latest block, difficulty, estimated computing power, and whether recent blocks are arriving fast or slow.",
            ),
            (
                "Verify",
                "Downloads the raw block, separates the 80-byte header, and checks whether the hash satisfies the Proof of Work rule.",
            ),
            (
                "Contextualize",
                "Shows that difficulty is not fixed: it changes every 2016 blocks to compensate for mining power.",
            ),
            (
                "Investigate",
                "The times between blocks are converted into features, and an unsupervised model marks unusual cases.",
            ),
        ]
    )
    st.markdown("#### What each part teaches")
    styled_table(
        pd.DataFrame(
            {
            "Part": ["Live network", "Inside a block", "Difficulty", "AI anomalies"],
            "Main question": [
                "What is happening on the Bitcoin network right now?",
                "How can we check that a block did real work?",
                "Why does difficulty go up or down over time?",
                "Which block intervals are unusual and worth reviewing?",
            ],
            "Key idea": [
                "The cost of mining can be observed through difficulty, hash rate, and intervals.",
                "A block can be verified by recalculating its hash.",
                "The protocol corrects the rhythm without a central authority.",
                "AI helps prioritize uncommon timing patterns.",
            ],
            }
        )
    )
    takeaway(
        "The important part is not memorizing the numbers.",
        "The important part is understanding the reasoning chain: real data, local verification, adjustment mechanism, and pattern analysis. "
        "That is the difference between showing isolated data and explaining Bitcoin.",
        tone="success",
    )

elif selected_page == "Live network":
    render_m1()

elif selected_page == "Inside a block":
    render_m2()

elif selected_page == "Difficulty":
    render_m3()

elif selected_page == "AI anomalies":
    render_m4()
