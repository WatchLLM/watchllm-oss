# watchllm-webproof

Public Python SDK for recording privacy-minimized HTTP request outcomes and producing a deterministic local Merkle summary.

> **Important:** `local_merkle_stub` is a local, non-attesting SHA-256 accumulator. It is **not** a TLS proof, remote-data proof, or cryptographic attestation. `reclaim` and `tlsnotary` values are declarative routing metadata only; this package contains no proof engine.

## Quickstart

```bash
pip install watchllm-webproof
watchllm verify-url https://api.example.com/health --config config.json
# --config is optional:
watchllm verify-url https://api.example.com/health
```

```python
from watchllm_webproof import VerifiableAgent

# No configuration is required.
with VerifiableAgent() as agent:
    response = agent.get("https://api.example.com/health", stream=True)
    print(agent.proof())
    response.close()

# JSON is the primary configuration format.
with VerifiableAgent(config_path="config.json") as agent:
    response = agent.post("https://api.example.com/events", json={"ok": True})
```

Async and generic requests are also available:

```python
async with VerifiableAgent(config_path="config.json") as agent:
    response = await agent.apost("https://example.org/data", json={"value": 1}, stream=True)
    await response.aclose()
    other = await agent.arequest("DELETE", "https://example.org/data/1")
```

`get`, `post`, and `request` use `requests`; `aget`, `apost`, and `arequest` use `httpx`. Only HTTP and HTTPS are supported. The SDK never records headers, cookies, request/response bodies, URL credentials, or query strings. It records method, normalized domain, effective port, path, status/error type, and selected route metadata. Explicit streaming is never eagerly consumed.

## Configuration

See [`examples/webproof.json`](examples/webproof.json) for the exact JSON contract. YAML remains supported for convenience; see [`examples/webproof.yaml`](examples/webproof.yaml).

Configuration is strict: unknown keys, duplicate JSON/YAML keys, duplicate normalized domains, invalid types, unsupported sensitivity values, and out-of-range TTL/aggregation values are rejected. `metadata` and `options` mappings are explicit extension points and are preserved rather than interpreted or silently discarded.

- `version` must be `"1.0.0"`.
- `session_persistence: true` reuses clients and persists cookies. This is the default.
- `session_persistence: false` creates a fresh client per request, so cookies do not cross requests. For an unconsumed stream, its client stays alive until `response.close()` / `await response.aclose()`.
- Each route requires `domain`, `prover_mode`, and `sensitivity`. `session_ttl` is optional; when omitted its value is `None`, and when present it must be a positive integer of at most 2,592,000 seconds (30 days), not JSON/YAML `null`. Routes include subdomains on DNS label boundaries; the most-specific parent domain wins.
- Aggregation accepts `batch_size` (default `10`) and `timeout_seconds` (default `120`). These values validate the promised contract and are reserved for a future remote aggregator; local stub accumulation remains immediate.

A caller-supplied `requests.Session` or `httpx.AsyncClient` is never closed by the agent and requires persistence to be enabled. `config` (mapping or `WebProofConfig`) and `config_path` are mutually exclusive.

## Proof contract

`proof()` preserves these keys: `proof_type`, `proof_version`, `attestation`, `algorithm`, `aggregation_enabled`, `merkle_root`, `leaf_count`, and `session_id`. `attestation` is always `false` in this local stub. An empty session has the conventional SHA-256 digest of empty bytes. Records are deterministic for the same request outcomes; timestamps are intentionally excluded.

## Development

```bash
python -m pip install -e '.[test]'
python -m pytest
python -m build
```
