"""Deterministic local accumulator; this is not a remote cryptographic attestation."""

from __future__ import annotations

import hashlib
import json
from threading import Lock
from typing import Any, Mapping


def canonical_leaf(record: Mapping[str, Any]) -> bytes:
    return json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def leaf_hash(record: Mapping[str, Any]) -> bytes:
    return hashlib.sha256(b"watchllm-webproof-local-leaf-v1\0" + canonical_leaf(record)).digest()


def merkle_root(records: list[Mapping[str, Any]]) -> str:
    """Return a deterministic SHA-256 binary Merkle root, duplicating odd nodes."""
    if not records:
        return hashlib.sha256(b"").hexdigest()
    level = [leaf_hash(record) for record in records]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [
            hashlib.sha256(b"watchllm-webproof-local-node-v1\0" + level[i] + level[i + 1]).digest()
            for i in range(0, len(level), 2)
        ]
    return level[0].hex()


class LocalMerkleAccumulator:
    """Thread-safe state and proof generation for the explicitly local stub."""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []
        self._lock = Lock()

    def record(self, record: Mapping[str, Any]) -> None:
        with self._lock:
            self._records.append(dict(record))

    @property
    def records(self) -> tuple[Mapping[str, Any], ...]:
        with self._lock:
            return tuple(dict(record) for record in self._records)

    def proof(self, session_id: str) -> dict[str, Any]:
        records = list(self.records)
        return {
            "proof_type": "local_merkle_stub",
            "proof_version": "1.0.0",
            "attestation": False,
            "algorithm": "sha256-local-merkle-v1",
            "aggregation_enabled": True,
            "merkle_root": merkle_root(records),
            "leaf_count": len(records),
            "session_id": session_id,
        }
