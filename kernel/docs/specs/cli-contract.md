# CLI Contract

## Purpose

Defines the stable command-line interface used by editor hosts, scripts, and future save-path integrations.

## Primary command

```bash
python -m watchllm_kernel evaluate <file> --json --language <language> --mode enforce
```

## Stdin command

```bash
python -m watchllm_kernel evaluate --stdin --json --language <language> --mode enforce
```

## Required flags

- `evaluate`
- `--json`
- `--language`
- `--mode`

## Supported modes

- `enforce`
- `shadow`

## Supported languages

- `javascript`
- `typescript`
- `tsx`

## Exit codes

- `0`: evaluation allowed
- `1`: evaluation blocked
- `2`: CLI/input error

## JSON output

The JSON output is the serialised `KernelResult`.

Required top-level fields:

- `decision`
- `rule_results`
- `file_path`
- `language`
- `mode`

## Enforcement semantics

In enforce mode, any failing rule causes `BLOCK`.

In shadow mode, failing rule results are preserved but the top-level decision remains `ALLOW`.

## Logging semantics

Blocked evaluations are logged locally through the reporting module.

Logging must not pollute stdout.

JSON stdout remains machine-readable.

## Editor integration requirements

Editor hosts should:

1. pass the unsaved buffer through stdin,
2. specify language explicitly,
3. request JSON output,
4. block the save if exit code is `1`,
5. display violations from JSON output,
6. avoid parsing human-readable output.
