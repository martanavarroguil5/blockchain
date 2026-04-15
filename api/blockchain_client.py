from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


BLOCKSTREAM_BASE_URL = "https://blockstream.info/api"
MEMPOOL_BASE_URL = "https://mempool.space/api"


class BlockchainApiError(RuntimeError):
    """Raised when a blockchain API request fails."""


@dataclass(slots=True)
class BlockchainClient:
    timeout_seconds: int = 15
    base_url: str = BLOCKSTREAM_BASE_URL

    def _get_text(self, path: str) -> str:
        response = requests.get(
            f"{self.base_url}{path}",
            timeout=self.timeout_seconds,
            headers={"User-Agent": "cryptochain-analyzer-dashboard"},
        )
        if not response.ok:
            raise BlockchainApiError(
                f"Request failed for {path}: {response.status_code} {response.text[:200]}"
            )
        return response.text.strip()

    def _get_json(self, path: str) -> Any:
        response = requests.get(
            f"{self.base_url}{path}",
            timeout=self.timeout_seconds,
            headers={"User-Agent": "cryptochain-analyzer-dashboard"},
        )
        if not response.ok:
            raise BlockchainApiError(
                f"Request failed for {path}: {response.status_code} {response.text[:200]}"
            )
        return response.json()

    def get_latest_block_hash(self) -> str:
        return self._get_text("/blocks/tip/hash")

    def get_latest_block(self) -> dict[str, Any]:
        return self.get_block(self.get_latest_block_hash())

    def get_block(self, block_hash: str) -> dict[str, Any]:
        return self._get_json(f"/block/{block_hash}")

    def get_block_status(self, block_hash: str) -> dict[str, Any]:
        return self._get_json(f"/block/{block_hash}/status")

    def get_recent_blocks(self, start_height: int | None = None) -> list[dict[str, Any]]:
        path = "/blocks" if start_height is None else f"/blocks/{start_height}"
        return self._get_json(path)

    def get_recent_blocks_window(self, limit: int = 30) -> list[dict[str, Any]]:
        if limit <= 0:
            return []

        blocks: list[dict[str, Any]] = []
        next_height: int | None = None

        while len(blocks) < limit:
            batch = self.get_recent_blocks(start_height=next_height)
            if not batch:
                break
            blocks.extend(batch)
            next_height = int(batch[-1]["height"]) - 1

        return blocks[:limit]

    def get_block_raw(self, block_hash: str) -> bytes:
        response = requests.get(
            f"{self.base_url}/block/{block_hash}/raw",
            timeout=self.timeout_seconds,
            headers={"User-Agent": "cryptochain-analyzer-dashboard"},
        )
        if not response.ok:
            raise BlockchainApiError(
                f"Request failed for /block/{block_hash}/raw: {response.status_code}"
            )
        return response.content


def get_client() -> BlockchainClient:
    return BlockchainClient()
