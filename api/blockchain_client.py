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
    fallback_base_url: str = MEMPOOL_BASE_URL

    def _request(self, path: str, *, response_type: str) -> Any:
        errors: list[str] = []

        for base_url in (self.base_url, self.fallback_base_url):
            response = requests.get(
                f"{base_url}{path}",
                timeout=self.timeout_seconds,
                headers={"User-Agent": "cryptochain-analyzer-dashboard"},
            )
            if response.ok:
                if response_type == "text":
                    return response.text.strip()
                if response_type == "json":
                    return response.json()
                if response_type == "bytes":
                    return response.content
                raise ValueError(f"Unsupported response type: {response_type}")

            errors.append(f"{base_url}: {response.status_code} {response.text[:160]}")

            if response.status_code not in {429, 500, 502, 503, 504}:
                break

        raise BlockchainApiError(f"Request failed for {path}: {' | '.join(errors)}")

    def _get_text(self, path: str) -> str:
        return str(self._request(path, response_type="text"))

    def _get_json(self, path: str) -> Any:
        return self._request(path, response_type="json")

    def get_latest_block_hash(self) -> str:
        return self._get_text("/blocks/tip/hash")

    def get_latest_block(self) -> dict[str, Any]:
        return self.get_block(self.get_latest_block_hash())

    def get_block(self, block_hash: str) -> dict[str, Any]:
        return self._get_json(f"/block/{block_hash}")

    def get_block_hash_by_height(self, height: int) -> str:
        return self._get_text(f"/block-height/{height}")

    def get_block_by_height(self, height: int) -> dict[str, Any]:
        return self.get_block(self.get_block_hash_by_height(height))

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
        return bytes(self._request(f"/block/{block_hash}/raw", response_type="bytes"))


def get_client() -> BlockchainClient:
    return BlockchainClient()
