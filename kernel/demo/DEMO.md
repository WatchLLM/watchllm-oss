# watchllm_kernel demo runbook

A 60–90 second demo of the kernel alone. No network, no API key, no editor
extension: the kernel is the part that decides whether a write is allowed.

Everything below runs against the installed console script, not a source
checkout. The four rules are deterministic; the same input always produces the
same verdict.

## Setup

```sh
cd kernel
py -m venv .venv
. .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e .
watchllm-kernel --version
```

## The five checks

Run from `kernel/`. Each command prints JSON to stdout and nothing else.

```sh
FIX=tests/fixtures/rules

# 1. a live Stripe key in source -> BLOCK, exit 1
watchllm-kernel check --filepath $FIX/secrets/fail/hardcoded_stripe_secret.ts --json
echo "exit=$?"

# 2. the same key read from the environment -> ALLOW, exit 0
watchllm-kernel check --filepath $FIX/secrets/pass/env_stripe_secret.ts --json
echo "exit=$?"

# 3. child_process in a file that should not import it -> BLOCK, exit 1
watchllm-kernel check --filepath $FIX/forbidden_imports/fail/child_process_import.js --json
echo "exit=$?"

# 4. a database mutation before auth verification -> BLOCK, exit 1
watchllm-kernel check --filepath $FIX/auth_flow/fail/mutation_before_auth.ts --json
echo "exit=$?"

# 5. auth imports a db-internal module across a boundary -> BLOCK, exit 1
watchllm-kernel check --filepath $FIX/boundary/fail/auth_imports_db_internal.ts --json
echo "exit=$?"
```

The `evaluate` spelling from `docs/specs/cli-contract.md` is an alias for
`check`; use whichever the slide says, they are byte-identical.

## Shadow mode

Shadow mode runs every rule and preserves the failures, but returns `ALLOW`.
This is the mode an editor uses while a team is tuning thresholds.

```sh
watchllm-kernel check \
  --filepath $FIX/secrets/fail/hardcoded_stripe_secret.ts \
  --json --mode shadow
# decision: ALLOW, mode: shadow, rule_results[0].status: FAIL
echo "exit=$?"   # 0
```

## The editor contract

An editor sends the unsaved buffer over stdin and names the language, because
there is no path to infer it from.

```sh
printf 'const key = "sk_live_1234567890abcdef";' |
  watchllm-kernel check --stdin --language ts --json
echo "exit=$?"   # 1
```

If the language cannot be determined, the kernel refuses instead of guessing:

```sh
printf 'print("hi")' | watchllm-kernel check --stdin --json
echo "exit=$?"   # 2, stderr explains why
```

An unknown extension is the same kind of refusal:

```sh
watchllm-kernel check --filepath README.md --json
echo "exit=$?"   # 2
```

The distinction matters: `ALLOW` means "no violation in source I understood". A
file the kernel cannot parse must not be reported as safe, so it is an input
error.

## The log

Blocked evaluations are appended to `.watchllm/logs/violations.jsonl`, one JSON
object per line. stdout stays machine-readable.

```sh
tail -n 3 .watchllm/logs/violations.jsonl
```

## What not to claim

- `parse_status` is the constant `"not_recorded"`. Nothing computes it. A file
  with a syntax error is still checked and violations are still found; the log
  simply cannot tell you whether the parse was clean. This is a reporting gap,
  not an enforcement gap.
- The kernel is deterministic by design. It does not call a model. Do not
  present it as an LLM reviewer.
- The proxy/cloud endpoints from the older WatchLLM product are gone. Demo the
  kernel as a local pre-write gate, not as a service.
