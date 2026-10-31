"""Rust-backed deterministic local accumulator; not a remote attestation."""

from __future__ import annotations

import json
from typing import Any, Mapping

try:
    from ._native import NativeAccumulator, canonical_leaf
except ImportError as exc:  # pragma: no cover - exercised by source-tree import test
    raise ImportError(
        "watchllm-webproof requires its Rust native extension; install a platform wheel "
        "or build from source with Rust and maturin. No cryptographic fallback is used."
    ) from exc


def merkle_root(records: list[Mapping[str, Any]]) -> str:
    """Return the native engine's root for compatibility with the historical helper."""
    accumulator = LocalMerkleAccumulator()
    for record in records:
        accumulator.record(record)
    return accumulator.proof("")["merkle_root"]


class LocalMerkleAccumulator:
    """Thread-safe state and proof generation delegated to the Rust engine."""

    def __init__(self) -> None:
        self._native = NativeAccumulator()

    def record(self, record: Mapping[str, Any]) -> None:
        if not isinstance(record, dict):
            # The native boundary deliberately accepts concrete dicts only. Copying a
            # Mapping also freezes its current top-level state before validation.
            record = dict(record)
        self._native.record(record)

    @property
    def records(self) -> tuple[Mapping[str, Any], ...]:
        # Rust stores canonical bytes, not borrowed Python objects. Decoding creates
        # fresh snapshots, so callers cannot mutate accumulated commitments.
        return tuple(json.loads(bytes(record)) for record in self._native.records_json())

    def proof(self, session_id: str) -> dict[str, Any]:
        return self._native.proof(session_id)


__all__ = ["LocalMerkleAccumulator", "canonical_leaf", "merkle_root"]
