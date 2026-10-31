# CLI Contract

## Purpose

Defines the stable command-line interface used by editor hosts, scripts, and
future save-path integrations.

## Primary command

```bash
python -m watchllm_kernel check --filepath <file> --json --language <language> --mode enforce
```

`evaluate` is accepted as an alias for `check`; the two are identical.

The file is passed with `--filepath`, not as a positional argument. There is no
positional form.

## Stdin command

```bash
python -m watchllm_kernel check --stdin --json --language <language> --mode enforce
```

## Required flags

- one of `--filepath <file>` or `--stdin`
- `--json`
- `--language` — required with `--stdin`. With `--filepath` it may be omitted,
  in which case it is inferred from the extension.
- `--mode`

## Language resolution

| Input | Result |
|---|---|
| `--language js` / `javascript` | `javascript` |
| `--language ts` / `typescript` | `typescript` |
| `--language tsx` | `tsx` |
| `.js` `.jsx` `.mjs` `.cjs` | `javascript` |
| `.ts` | `typescript` |
| `.tsx` | `tsx` |
| anything else, with no `--language` | exit code `2` |

An unrecognised extension is **not** evaluated as JavaScript. Reporting `ALLOW`
for a file that was never parsed would make the gate lie: `ALLOW` means "no
violation found in source I understood", so a file the kernel cannot understand
must be an input error, not an allow.

## Supported modes

- `enforce`
- `shadow`

## Exit codes

- `0`: evaluation allowed
- `1`: evaluation blocked
- `2`: CLI/input error (unreadable file, undeterminable language, bad arguments)

## JSON output

The JSON output is the serialised `KernelResult`.

Required top-level fields:

- `decision`
- `rule_results`
- `file_path`
- `language`
- `mode`

`language` is the resolved parser language (`javascript`, `typescript`, or
`tsx`), not the flag value.

## Enforcement semantics

In enforce mode, any failing rule causes `BLOCK`.

In shadow mode, failing rule results are preserved but the top-level decision
remains `ALLOW`.

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
6. avoid parsing human-readable output,
7. treat exit code `2` as "not evaluated", never as "safe".

## Known gaps

- `parse_status` in the violation log is currently the constant
  `not_recorded`; nothing computes it, so the log cannot distinguish a clean
  parse from a partial one. Enforcement is unaffected — a file with an error
  node is still checked, and violations are still found.
