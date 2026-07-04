# Phase 3 — Schemas Audit

## Date: 2026-06-15

## Summary
Audited the `watchllm/schemas` repo — the central JSON Schema contracts for the WatchLLM ecosystem. Found 4 issues (2 CRITICAL, 1 MODERATE, 1 LOW). All fixed.

## Issues Found & Fixed

### 1. ❌ CRITICAL — Severity enum mismatch
**Before:** `violation.json` severity enum was `["CRITICAL", "WARNING", "INFO"]` only.
**Reality:** Python kernel defines `CRITICAL | HIGH | MEDIUM | LOW | INFO` and Rust runtime uses freeform strings (`"error"`, `"warning"`, `"info"`).
**Fix:** Updated schema to accept both the Python canonical enum (`CRITICAL | HIGH | MEDIUM | LOW | INFO`) AND the Rust short forms (`error | warning | info`) using `oneOf`.

### 2. ❌ CRITICAL — Missing KernelExecutionResult schema
**Before:** No schema for the actual cross-component JSON contract.
**Reality:** The Rust runtime (Wasm + CLI) emits `KernelExecutionResult { status, exit_code, payload: { allowed, violations }, error }`. This is consumed by VSCode, Klyd, Replay, and the Orchestrator. No schema existed for it.
**Fix:** Created `schemas/v1/kernel_execution_result.json` with full Draft-07 definitions including `$ref` → `violation.json`.

### 3. ⚠️ MODERATE — Decision schema structural gap
**Before:** `decision.json` had a flat `violations` array at the top level.
**Reality:** Python `KernelResult` emits `rule_results` (list of `{rule_id, decision, violations}` objects), not a flat violations list.
**Fix:** Changed `decision.json` to match the actual Python kernel output shape with `rule_results` array. Added `INCONCLUSIVE` to the `decision` enum. Added `file_path` and `mode` back.

### 4. ⚠️ LOW — Missing `evidence` field in violation schema
**Before:** No `evidence` field.
**Reality:** Python `Violation` dataclass has `evidence: Optional[str]`.
**Fix:** Added optional `evidence` field.

### 5. ℹ️ INFO — Event schema is aspirational
`event.json` defines event types (`parse_started`, `parse_completed`, `violation_detected`, `save_blocked`, `save_allowed`) that no component currently emits. The schema is valid Draft-07 but has zero consumers. Retained as-is (forward-looking contract).

### 6. Fixed — `location` nullability
Python kernel emits `"location": null` for violations without location info. Original schema required `type: "object"`. Fixed to `oneOf: [{ type: "null" }, { type: "object", ... }]`.

## Validation Results
- All 4 schemas pass `jsonschema.Draft7Validator.check_schema()`
- Python `KernelResult` output validates against `decision.json`
- Rust `KernelExecutionResult` output validates against `kernel_execution_result.json`
- Both allowed and blocked outputs from both runtimes validate successfully

## Changed Files
- `schemas/v1/violation.json` — severity enum fix, location nullability, evidence field, dual rule_id/rule support
- `schemas/v1/decision.json` — rule_results structure, INCONCLUSIVE enum value
- `schemas/v1/kernel_execution_result.json` — NEW: cross-component contract schema
- `schemas/v1/event.json` — unchanged