from __future__ import annotations

import hashlib


def bits_to_target(bits: int) -> int:
    exponent = bits >> 24
    mantissa = bits & 0xFFFFFF
    if exponent <= 3:
        return mantissa >> (8 * (3 - exponent))
    return mantissa << (8 * (exponent - 3))


def estimate_hash_rate_hs(difficulty: float) -> float:
    return difficulty * (2**32) / 600


def human_hash_rate(hash_rate_hs: float) -> str:
    units = ["H/s", "kH/s", "MH/s", "GH/s", "TH/s", "PH/s", "EH/s", "ZH/s"]
    value = float(hash_rate_hs)
    for unit in units:
        if value < 1000 or unit == units[-1]:
            return f"{value:,.2f} {unit}"
        value /= 1000
    return f"{value:,.2f} ZH/s"


def leading_zero_bits(value: int, width: int = 256) -> int:
    if value <= 0:
        return width
    return max(0, width - value.bit_length())


def double_sha256(payload: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(payload).digest()).digest()


def bitcoin_hash_hex(digest: bytes) -> str:
    return digest[::-1].hex()
