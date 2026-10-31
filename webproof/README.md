# watchllm-webproof

Public Python SDK for recording privacy-minimized HTTP request outcomes and producing a deterministic local Merkle commitment. Canonical serialization and incremental SHA-256 Merkle construction are owned by a pure Rust core exposed through separate PyO3 and WebAssembly adapters.

> **Important:** `local_merkle_stub` is a local, non-attesting SHA-256 accumulator. It is **not** a TLS proof, remote-data proof, or cryptographic attestation. `reclaim` and `tlsnotary` values are declarative routing metadata only; this package contains no remote prover or verifier. Cloud submission, when explicitly requested, stores and anchors this commitment; it does not upgrade those semantics.

## Quickstart

```bash
pip install watchllm-webproof
watchllm verify-url https://api.example.com/health --config config.json
# --config is optional:
watchllm verify-url https://api.example.com/health
```

```python
from watchllm_webproof import VerifiableAgent

with VerifiableAgent() as agent:
    response = agent.get("https://api.example.com/health", stream=True)
    print(agent.proof())
    response.close()

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

## Explicit cloud submission

Local-only operation remains the default: constructing an agent, making requests, calling `proof()`, and running `watchllm verify-url URL` never contact WebProof Edge. Remote I/O requires an explicit `CloudClient` call or CLI `--submit`/`cloud-status` command. Endpoints must use HTTPS, redirects are disabled, and API keys are read from an environment variable by the CLI and are never included in output, response bodies, or SDK exception messages.

```bash
export WATCHLLM_API_KEY='key_id.secret'
watchllm verify-url https://api.example.com/health \
  --submit https://webproof-edge.example \
  --response-hash 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef \
  --poll-timeout 30
watchllm cloud-status VERIFICATION_UUID --endpoint https://webproof-edge.example --poll-timeout 30
```

`--submit` sends strict envelope v1 to `POST /proof` and prints its verification ID/status. Edge may return `stored` when its explicit anchoring mode is disabled: this means D1/R2 persistence only, not queued, submitted, anchored, verified, or attested. `--poll-timeout` treats `stored` as nonterminal and polls with bounded exponential backoff; timeout returns the latest nonterminal status rather than polling indefinitely. `--chain base-mainnet` is always explicit; omission lets Edge use its configured default.

The Python interface separates envelope construction from network access:

```python
import time
from watchllm_webproof import CloudClient, build_edge_envelope

# agent has already recorded one or more outcomes
payload = build_edge_envelope(
    agent.records,
    agent.proof(),
    leaf_index=0,
    response_hash="01" * 32,
    observed_at=int(time.time() * 1000),
)
with CloudClient("https://webproof-edge.example", api_key) as cloud:
    result = cloud.submit(payload)
    result = cloud.poll(result.verification_id, timeout=30)
```

Envelope v1 has a semantic limitation worth making explicit: native records commit to request outcome metadata but intentionally contain neither response bytes nor timestamps. Edge nevertheless requires `response_hash` and `observed_at`; callers must supply them, and Edge stores them with `metadata_bound=0`. They are compatibility metadata **not bound by the selected leaf and not attested**. The uploaded canonical payload contains the native proof and all native record snapshots; the selected record supplies `target_domain` and path, and the SDK derives its inclusion path using the exact Rust leaf/node domain contract.

## Native engine and installation

Published wheels contain the native Rust extension for their declared Python version and platform. There is intentionally **no Python cryptographic fallback**: importing from an unbuilt source checkout fails with a clear error rather than silently changing commitment behavior.

A source install requires Python 3.10+, a Rust toolchain (Rust 1.74 or newer), and a working native compiler. The PEP 517 build frontend installs the pinned-compatible `maturin` build backend automatically:

```bash
python -m pip install .
```

The canonical commitment contract is byte-for-byte compatible with Python's historical `json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True)` for supported values. Supported values are null, booleans, arbitrary-size integers, strings without lone surrogates, lists/tuples, and dictionaries with string keys. Floats and other Python objects are rejected to avoid non-portable commitments. Circular references and nesting beyond 128 child edges are rejected before canonical serialization, protecting the native stack while preserving deterministic output at every supported depth. Golden vectors live in `tests/vectors/commitment-v1.json`. The core keeps one completed subtree per set bit in the leaf count, so append and root retrieval use O(log n) hashes and O(log n) hash storage. Root folding intentionally reproduces the historical algorithm: at every level with an unpaired rightmost node, that node is duplicated before promotion. This matters for non-power-of-two counts (including duplication at multiple levels) and is regression-tested against the original full-tree rebuild at every deterministic-vector prefix and across generated inputs.

The native extension targets CPython. A release must build and test wheels for each supported OS, architecture, and CPython version before publishing; a source distribution alone is not a substitute for that wheel matrix.

## Configuration

See [`examples/webproof.json`](examples/webproof.json) for the exact JSON contract. YAML remains supported for convenience; see [`examples/webproof.yaml`](examples/webproof.yaml).

Configuration is strict: unknown keys, duplicate JSON/YAML keys, duplicate normalized domains, invalid types, unsupported sensitivity values, and out-of-range TTL/aggregation values are rejected. `metadata` and `options` mappings are explicit extension points and are preserved rather than interpreted or silently discarded.

- `version` must be `"1.0.0"`.
- `session_persistence: true` reuses clients and persists cookies. This is the default.
- `session_persistence: false` creates a fresh client per request, so cookies do not cross requests. For an unconsumed stream, its client stays alive until `response.close()` / `await response.aclose()`.
- Each route requires `domain`, `prover_mode`, and `sensitivity`. `session_ttl` is optional; when omitted its value is `None`, and when present it must be a positive integer of at most 2,592,000 seconds (30 days), not JSON/YAML `null`. Routes include subdomains on DNS label boundaries; the most-specific parent domain wins.
- Aggregation accepts `batch_size` (default `10`) and `timeout_seconds` (default `120`). These values validate the promised contract and are reserved for a future remote aggregator; local accumulation remains immediate.

A caller-supplied `requests.Session` or `httpx.AsyncClient` is never closed by the agent and requires persistence to be enabled. `config` (mapping or `WebProofConfig`) and `config_path` are mutually exclusive.

## Proof contract

`proof()` preserves these keys: `proof_type`, `proof_version`, `attestation`, `algorithm`, `aggregation_enabled`, `merkle_root`, `leaf_count`, and `session_id`. `attestation` is always `false`. An empty session has the conventional SHA-256 digest of empty bytes. Records are deterministic for the same request outcomes; timestamps are intentionally excluded.

## Development

```bash
python -m pip install -e '.[test]'
cargo fmt --manifest-path engine/Cargo.toml --all -- --check
cargo clippy --manifest-path engine/Cargo.toml --all-targets --locked -- -D warnings
cargo test --manifest-path engine/Cargo.toml --locked
cargo build --manifest-path engine/Cargo.toml --target wasm32-unknown-unknown \
  --release --no-default-features --features wasm
cd engine/wasm && npm run build && npm test
python -m pytest
python -m build
```

## WebAssembly API

The `wasm` feature builds a real `wasm-bindgen` API without linking PyO3. `canonical_leaf_json(recordJson)` and `WasmAccumulator.append_json(recordJson)` accept JSON text rather than JavaScript objects; this avoids rounding integers such as `9007199254740993` before Rust receives them. `WasmAccumulator.root_hex()` and `leaf_count()` expose the same commitment state as Python/native. Floats and non-object records are rejected. `engine/wasm/parity.test.mjs` consumes the shared Python/native golden vectors and tests the generated Node.js WebAssembly package.
