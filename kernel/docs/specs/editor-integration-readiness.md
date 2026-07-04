# Editor Integration Readiness

## Purpose

Defines how the current Python kernel can be called by an editor save hook before a native Wasm runtime exists.

## Current integration mode

The editor host should call the CLI as a subprocess.

Recommended save-path command:

```bash
python -m watchllm_kernel evaluate --stdin --json --language typescript --mode enforce
```

The unsaved document text must be passed to stdin.

## Required editor behaviour

- Run evaluation before save completion.
- Treat exit code `1` as save-blocking.
- Treat exit code `0` as save-allowing.
- Treat exit code `2` as CLI/input error and surface it clearly.
- Parse stdout only as JSON when `--json` is used.
- Do not rely on human-readable output for enforcement.
- Do not require network access.

## Current guarantees

- Local-only execution.
- Deterministic rule evaluation.
- Enforce/shadow mode support.
- JSON output.
- Local blocked-event JSONL logging.

## Current limitations

- The Python subprocess has startup overhead.
- Save interception itself is not implemented in this repository.
- Parse status in reports is currently `not_recorded`.
- Rule modules support independent parsing, but CLI/engine integration now parses
  once and shares a single parse result across rules.
- Wasm/native editor embedding is future work.

## Non-goals

- VSCode extension implementation.
- Editor UI diagnostics.
- Wasm runtime.
- Cloud policy sync.
- Remote telemetry.
