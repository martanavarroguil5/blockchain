from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import pandas as pd
import streamlit as st

from api.blockchain_client import BlockchainApiError, get_client
from modules.bitcoin_math import bitcoin_hash_hex, bits_to_target, double_sha256, leading_zero_bits
from modules.ui import concept_flow, metric_explainer_grid, module_header, story_panel, styled_table, takeaway


@dataclass(frozen=True, slots=True)
class ParsedBlockHeader:
    raw_hex: str
    version: int
    previous_hash: str
    merkle_root: str
    timestamp: int
    bits: int
    nonce: int
    local_hash: str
    hash_value: int
    target: int

    @property
    def timestamp_utc(self) -> str:
        return datetime.fromtimestamp(self.timestamp, UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    @property
    def target_hex(self) -> str:
        return f"{self.target:064x}"

    @property
    def is_valid_pow(self) -> bool:
        return self.hash_value <= self.target


def parse_block_header(header: bytes) -> ParsedBlockHeader:
    if len(header) != 80:
        raise ValueError(f"Expected an 80-byte Bitcoin block header, got {len(header)} bytes.")

    version = int.from_bytes(header[0:4], "little", signed=True)
    previous_hash = header[4:36][::-1].hex()
    merkle_root = header[36:68][::-1].hex()
    timestamp = int.from_bytes(header[68:72], "little")
    bits = int.from_bytes(header[72:76], "little")
    nonce = int.from_bytes(header[76:80], "little")
    digest = double_sha256(header)
    local_hash = bitcoin_hash_hex(digest)

    return ParsedBlockHeader(
        raw_hex=header.hex(),
        version=version,
        previous_hash=previous_hash,
        merkle_root=merkle_root,
        timestamp=timestamp,
        bits=bits,
        nonce=nonce,
        local_hash=local_hash,
        hash_value=int.from_bytes(digest, "little"),
        target=bits_to_target(bits),
    )


@st.cache_data(ttl=60, show_spinner=False)
def load_latest_header() -> tuple[dict[str, object], ParsedBlockHeader]:
    client = get_client()
    latest_block = client.get_latest_block()
    raw_block = client.get_block_raw(str(latest_block["id"]))
    parsed_header = parse_block_header(raw_block[:80])
    return latest_block, parsed_header


def render_m2() -> None:
    module_header(
        "Inside a block",
        "Anatomy of a valid block",
        "Downloads the latest block, separates its 80-byte header, and locally verifies its Proof of Work.",
    )

    try:
        latest_block, header = load_latest_header()
    except BlockchainApiError as exc:
        st.error(f"Could not load the latest block from public sources: {exc}")
        return
    except Exception as exc:
        st.error(f"Unexpected error while verifying the header: {exc}")
        return

    hash_matches_api = header.local_hash == latest_block["id"]
    valid_pow = header.is_valid_pow and hash_matches_api

    story_panel(
        "Why look at the header",
        "The header is the small part of the block that concentrates the cryptographic proof.",
        "A full block can contain many transactions, but miners do not test the whole block over and over: "
        "they work on an 80-byte header. If the double SHA-256 of that header is below the target, the block proves work.",
        [
            "The previous hash connects this block to the chain.",
            "The Merkle root is a cryptographic summary of all transactions in the block.",
            "PoW verification checks that the header hash satisfies the difficulty target.",
            "The nonce is one of the fields the miner can change to search for a valid hash.",
        ],
    )
    concept_flow(
        [
            ("Download", "The raw block is obtained from a public Bitcoin source."),
            ("Separate", "The first 80 bytes are taken; they form the header."),
            ("Hash", "SHA256(SHA256(header)) is calculated locally."),
            ("Compare", "The result must match the published block and be lower than the target."),
        ]
    )

    metric_explainer_grid(
        [
            (
                "Height",
                f"{int(latest_block['height']):,}",
                "Block number counted from the first Bitcoin block.",
            ),
            (
                "Header size",
                "80 bytes",
                "Small part that is hashed to prove work.",
            ),
            (
                "Leading zeros",
                str(leading_zero_bits(header.hash_value)),
                "Zero bits at the start of the hash: a sign that the hash is very small.",
            ),
            (
                "PoW verification",
                "Valid" if valid_pow else "Review",
                "The hash calculated here matches the published one and is below the target.",
            ),
        ]
    )
    st.write(
        "The key metric is PoW verification. If it appears as valid, it means this app has recalculated the block hash "
        "and checked that it satisfies the rule: the numeric hash value is below the difficulty target."
    )

    st.markdown("#### The six header fields")
    st.write(
        "These are the exact data fields that enter the hash. The table is not decorative: it lets you audit what information is being verified."
    )
    field_rows = [
        ("Version", str(header.version), "Format/rules used by the block"),
        ("Previous hash", header.previous_hash, "Cryptographic link to the previous block"),
        (
            "Merkle root",
            header.merkle_root,
            "Summary hash of the transactions: it helps detect whether any transaction in the block changed.",
        ),
        ("Timestamp", f"{header.timestamp} ({header.timestamp_utc})", "Time declared by the miner"),
        ("Bits", f"{header.bits} / 0x{header.bits:08x}", "Difficulty target in compact format"),
        ("Nonce", str(header.nonce), "Value that helps search for a valid hash"),
    ]
    styled_table(
        pd.DataFrame(field_rows, columns=["Field", "Value", "Meaning"]),
    )

    st.markdown("#### Local verification with double SHA-256")
    st.write(
        "This part checks the block step by step. First, the app calculates the header hash again. "
        "Then it checks whether that hash matches the official block hash. Finally, it checks the difficulty rule: "
        "the hash must be lower than the target. If both comparisons pass, the Proof of Work is valid."
    )
    st.code("hash = SHA256(SHA256(80-byte header))", language="text")
    st.markdown("#### How to read the check")
    st.write(
        "The two boxes on the left must be identical. That shows the hash has been reproduced correctly. "
        "The box on the right shows the maximum limit allowed by difficulty; the result `Yes` means the hash is below that limit."
    )
    verify_col_1, verify_col_2 = st.columns(2)
    with verify_col_1:
        st.write("Official block hash")
        st.code(str(latest_block["id"]), language="text")
        st.write("Hash recalculated by this app")
        st.code(header.local_hash, language="text")
    with verify_col_2:
        st.write("Maximum allowed target")
        st.code(header.target_hex, language="text")
        st.write("The hash is below that target")
        st.success("Yes" if header.hash_value <= header.target else "No")

    if valid_pow:
        takeaway(
            "The block passes verification.",
            "The locally calculated hash matches the published hash and is also below the target. That is exactly what it means for the block to have valid Proof of Work.",
            tone="success",
        )
    else:
        st.error("Local verification failed. The byte order, raw block, or public source response should be reviewed.")

    with st.expander("Raw 80-byte header"):
        st.code(header.raw_hex, language="text")
