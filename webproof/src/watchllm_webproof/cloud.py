"""Explicit WebProof Edge submission; importing or constructing this module performs no I/O."""

from __future__ import annotations

import base64
import hashlib
import json
import math
import time
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import quote, urlsplit

import requests

from .accumulator import canonical_leaf
from .exceptions import CloudSubmissionError

_LEAF_DOMAIN = b"watchllm-webproof-local-leaf-v1\0"
_NODE_DOMAIN = b"watchllm-webproof-local-node-v1\0"
_TERMINAL_STATUSES = frozenset({"anchored", "failed"})
_KNOWN_STATUSES = frozenset({"stored", "queued", "processing", "submitted", "anchored", "failed"})
_MAX_PAYLOAD_BYTES = 1_048_576
_PUBLIC_RESPONSE_FIELDS = frozenset({
    "verification_id", "status", "verification_mode", "attestation", "envelope_version",
    "proof_type", "proof_version", "merkle_root", "payload_digest", "chain",
    "l2_transaction_hash", "tx_hash", "confirmations", "required_confirmations", "error",
    "created_at", "updated_at", "anchoring_mode",
})


def _sha256(value: bytes) -> bytes:
    return hashlib.sha256(value).digest()


def _node_hash(left: bytes, right: bytes) -> bytes:
    return _sha256(_NODE_DOMAIN + left + right)


def _leaf_hash(record: Mapping[str, Any]) -> bytes:
    return _sha256(_LEAF_DOMAIN + bytes(canonical_leaf(record)))


def _inclusion_path(records: Sequence[Mapping[str, Any]], leaf_index: int) -> tuple[str, list[str]]:
    if not records:
        raise ValueError("cannot submit an empty proof")
    if isinstance(leaf_index, bool) or not isinstance(leaf_index, int):
        raise TypeError("leaf_index must be an integer")
    if leaf_index < 0 or leaf_index >= len(records):
        raise ValueError("leaf_index is outside the recorded leaf range")

    level = [_leaf_hash(record) for record in records]
    selected_hash = level[leaf_index].hex()
    index = leaf_index
    path: list[str] = []
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        path.append(level[index ^ 1].hex())
        level = [_node_hash(level[offset], level[offset + 1]) for offset in range(0, len(level), 2)]
        index //= 2
    return selected_hash, path


def build_edge_envelope(
    records: Sequence[Mapping[str, Any]],
    proof: Mapping[str, Any],
    *,
    leaf_index: int,
    response_hash: str,
    observed_at: int,
    chain: str | None = None,
) -> dict[str, Any]:
    """Build strict Edge envelope v1 from native record snapshots and proof output.

    ``response_hash`` and ``observed_at`` are explicit because the local commitment
    intentionally does not record response bytes or timestamps. Edge stores this
    metadata as unbound compatibility metadata; it is not attested by the leaf.
    """
    required = {
        "proof_type": "local_merkle_stub",
        "proof_version": "1.0.0",
        "attestation": False,
        "algorithm": "sha256-local-merkle-v1",
    }
    if any(proof.get(key) != value for key, value in required.items()):
        raise ValueError("proof is not a supported native local commitment")
    if proof.get("leaf_count") != len(records):
        raise ValueError("proof leaf_count does not match records")
    session_id = proof.get("session_id")
    if not isinstance(session_id, str) or not 1 <= len(session_id.encode("utf-8")) <= 64:
        raise ValueError("proof session_id must be 1-64 UTF-8 bytes for Edge envelope v1")
    merkle_root = proof.get("merkle_root")
    if not isinstance(merkle_root, str) or not _is_hash(merkle_root):
        raise ValueError("proof merkle_root must be a 32-byte hex string")
    if not _is_hash(response_hash):
        raise ValueError("response_hash must be a 32-byte hex string")
    if isinstance(observed_at, bool) or not isinstance(observed_at, int):
        raise TypeError("observed_at must be an integer Unix timestamp in milliseconds")
    if observed_at < 946_684_800_000 or observed_at > int(time.time() * 1000) + 300_000:
        raise ValueError("observed_at is outside the plausible millisecond range")
    if chain not in {None, "base-sepolia", "base-mainnet"}:
        raise ValueError("chain must be base-sepolia or base-mainnet")

    record = records[leaf_index] if 0 <= leaf_index < len(records) else None
    leaf_hash, merkle_path = _inclusion_path(records, leaf_index)
    if record is None:  # pragma: no cover - range is enforced above
        raise ValueError("leaf_index is outside the recorded leaf range")
    domain = record.get("domain")
    path = record.get("path")
    if not isinstance(domain, str) or not isinstance(path, str):
        raise ValueError("selected native record has no domain/path metadata")

    payload = json.dumps(
        {"proof": dict(proof), "records": [dict(item) for item in records]},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    if len(payload) > _MAX_PAYLOAD_BYTES:
        raise ValueError("canonical proof payload exceeds Edge's 1 MiB decoded limit")

    envelope: dict[str, Any] = {
        "envelope_version": "1",
        "proof_version": "1.0.0",
        "proof_type": "local_merkle_stub",
        "verification_mode": "commitment_only",
        "attestation": False,
        "merkle_root": merkle_root,
        "leaf_hash": leaf_hash,
        "leaf_index": leaf_index,
        "merkle_path": merkle_path,
        "session_id": session_id,
        "leaf_data": {
            "target_domain": domain,
            "path": path,
            "response_hash": response_hash.removeprefix("0x").lower(),
            "timestamp": observed_at,
        },
        "proof_payload": base64.b64encode(payload).decode("ascii"),
    }
    if chain is not None:
        envelope["chain"] = chain
    return envelope


def _is_hash(value: str) -> bool:
    normalized = value.removeprefix("0x")
    return len(normalized) == 64 and all(character in "0123456789abcdefABCDEF" for character in normalized)


@dataclass(frozen=True)
class CloudResult:
    """Validated public status returned by WebProof Edge."""

    verification_id: str
    status: str
    data: Mapping[str, Any]


class CloudClient:
    """Opt-in authenticated client for WebProof Edge POST/GET operations."""

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        *,
        timeout: float = 30.0,
        session: requests.Session | None = None,
        sleep: Callable[[float], None] = time.sleep,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        parsed = urlsplit(endpoint)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("cloud endpoint must be an HTTPS URL without credentials")
        if parsed.query or parsed.fragment:
            raise ValueError("cloud endpoint must not contain a query or fragment")
        if not api_key or len(api_key) > 512 or "." not in api_key or any(character.isspace() for character in api_key):
            raise ValueError("api_key must be a non-empty key_id.secret bearer token")
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("timeout must be a positive finite number")
        self._endpoint = endpoint.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout
        self._session = session or requests.Session()
        self._owns_session = session is None
        self._sleep = sleep
        self._monotonic = monotonic

    def __enter__(self) -> "CloudClient":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    def close(self) -> None:
        if self._owns_session:
            self._session.close()

    def submit(self, envelope: Mapping[str, Any]) -> CloudResult:
        response = self._request("POST", f"{self._endpoint}/proof", json=dict(envelope))
        if response.status_code != 202:
            raise CloudSubmissionError(f"cloud submission failed with HTTP {response.status_code}")
        return self._result(response)

    def status(self, verification_id: str) -> CloudResult:
        return self._status(verification_id, request_timeout=self._timeout)

    def _status(self, verification_id: str, *, request_timeout: float) -> CloudResult:
        if not _is_uuid(verification_id):
            raise ValueError("verification_id must be a UUID")
        response = self._request(
            "GET",
            f"{self._endpoint}/proof/{quote(verification_id, safe='')}",
            request_timeout=request_timeout,
        )
        if response.status_code != 200:
            raise CloudSubmissionError(f"cloud status request failed with HTTP {response.status_code}")
        return self._result(response, expected_id=verification_id)

    def poll(
        self,
        verification_id: str,
        *,
        timeout: float,
        initial_interval: float = 0.25,
        max_interval: float = 5.0,
    ) -> CloudResult:
        """Poll until anchored/failed or return the latest status at the deadline."""
        for name, value in (("timeout", timeout), ("initial_interval", initial_interval), ("max_interval", max_interval)):
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be a positive finite number")
        deadline = self._monotonic() + timeout
        interval = min(initial_interval, max_interval)
        latest: CloudResult | None = None
        while True:
            remaining = deadline - self._monotonic()
            if remaining <= 0:
                if latest is not None:
                    return latest
                raise CloudSubmissionError("cloud polling deadline expired before a status response")
            result = self._status(verification_id, request_timeout=min(self._timeout, remaining))
            latest = result
            if result.status in _TERMINAL_STATUSES:
                return result
            remaining = deadline - self._monotonic()
            if remaining <= 0:
                return result
            self._sleep(min(interval, remaining))
            interval = min(interval * 2, max_interval)

    def _request(
        self,
        method: str,
        url: str,
        *,
        request_timeout: float | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        try:
            return self._session.request(
                method,
                url,
                headers={"Authorization": f"Bearer {self._api_key}", "Accept": "application/json"},
                timeout=self._timeout if request_timeout is None else request_timeout,
                allow_redirects=False,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise CloudSubmissionError(f"cloud request failed ({type(exc).__name__})") from None

    @staticmethod
    def _result(response: requests.Response, expected_id: str | None = None) -> CloudResult:
        try:
            data = response.json()
        except (ValueError, requests.JSONDecodeError):
            raise CloudSubmissionError("cloud response was not valid JSON") from None
        if not isinstance(data, dict):
            raise CloudSubmissionError("cloud response must be a JSON object")
        verification_id = data.get("verification_id")
        status = data.get("status")
        if not isinstance(verification_id, str) or not _is_uuid(verification_id):
            raise CloudSubmissionError("cloud response contained an invalid verification_id")
        if expected_id is not None and verification_id != expected_id:
            raise CloudSubmissionError("cloud response verification_id did not match the request")
        if status not in _KNOWN_STATUSES:
            raise CloudSubmissionError("cloud response contained an invalid status")
        public_data = {key: value for key, value in data.items() if key in _PUBLIC_RESPONSE_FIELDS}
        return CloudResult(verification_id, status, public_data)


def _is_uuid(value: str) -> bool:
    import re

    return re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", value) is not None


__all__ = ["CloudClient", "CloudResult", "build_edge_envelope"]
