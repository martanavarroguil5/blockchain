from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import pandas as pd
import streamlit as st

from api.blockchain_client import BlockchainApiError, get_client
from modules.bitcoin_math import bitcoin_hash_hex, bits_to_target, double_sha256, leading_zero_bits


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
    st.subheader("M2 - Block Header Analyzer")
    st.caption("Latest Bitcoin block header parsed from raw bytes and verified locally.")

    try:
        latest_block, header = load_latest_header()
    except BlockchainApiError as exc:
        st.error(f"Could not load the latest block header: {exc}")
        return
    except Exception as exc:
        st.error(f"Unexpected error while verifying the block header: {exc}")
        return

    hash_matches_api = header.local_hash == latest_block["id"]
    valid_pow = header.is_valid_pow and hash_matches_api

    metric_col_1, metric_col_2, metric_col_3, metric_col_4 = st.columns(4)
    metric_col_1.metric("Block height", f"{int(latest_block['height']):,}")
    metric_col_2.metric("Header size", "80 bytes")
    metric_col_3.metric("Hash leading zero bits", str(leading_zero_bits(header.hash_value)))
    metric_col_4.metric("PoW verification", "Valid" if valid_pow else "Check failed")

    st.markdown("#### Six header fields")
    field_rows = [
        ("Version", str(header.version), "4 bytes, little-endian signed integer"),
        ("Previous block hash", header.previous_hash, "32 bytes, displayed in Bitcoin byte order"),
        ("Merkle root", header.merkle_root, "32 bytes, displayed in Bitcoin byte order"),
        ("Timestamp", f"{header.timestamp} ({header.timestamp_utc})", "4 bytes, Unix time"),
        ("Bits", f"{header.bits} / 0x{header.bits:08x}", "4 bytes, compact target encoding"),
        ("Nonce", str(header.nonce), "4 bytes, miner-selected value"),
    ]
    st.dataframe(
        pd.DataFrame(field_rows, columns=["Field", "Value", "Meaning"]),
        width="stretch",
        hide_index=True,
    )

    st.markdown("#### Local double SHA-256 verification")
    st.code("hash = SHA256(SHA256(80-byte header))", language="text")
    verify_col_1, verify_col_2 = st.columns(2)
    with verify_col_1:
        st.write("API block hash")
        st.code(str(latest_block["id"]), language="text")
        st.write("Locally computed block hash")
        st.code(header.local_hash, language="text")
    with verify_col_2:
        st.write("Target decoded from `bits`")
        st.code(header.target_hex, language="text")
        st.write("Hash value is below target")
        st.code(f"{header.hash_value <= header.target}", language="text")

    if valid_pow:
        st.success("The locally computed hash matches the API hash and is below the target threshold.")
    else:
        st.error("The local verification failed. Check byte order, raw header bytes, or API response.")

    with st.expander("Raw 80-byte header"):
        st.code(header.raw_hex, language="text")
