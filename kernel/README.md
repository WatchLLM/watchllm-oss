# WatchLLM Kernel

```
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░  ░░░░  ░░░      ░░░        ░░░      ░░░  ░░░░  ░░  ░░░░░░░░  ░░░░░░░░  ░░░░  ░
▒  ▒  ▒  ▒▒  ▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒▒▒▒▒   ▒▒   ▒
▓        ▓▓  ▓▓▓▓  ▓▓▓▓▓  ▓▓▓▓▓  ▓▓▓▓▓▓▓▓        ▓▓  ▓▓▓▓▓▓▓▓  ▓▓▓▓▓▓▓▓        ▓
█   ██   ██        █████  █████  ████  ██  ████  ██  ████████  ████████  █  █  █
█  ████  ██  ████  █████  ██████      ███  ████  ██        ██        ██  ████  █
████████████████████████████████████████████████████████████████████████████████
```

Deterministic local write-path governance kernel for autonomous coding agents.

## Current status

Task 14 complete — core model layer, parser abstraction, fixture corpus, rule implementations, deterministic decision engine, CLI evaluation interface, end-to-end regression tests, baseline performance benchmarks, and local blocked-event reporting exist. Save-path editor integration is not implemented yet.

## Installation

```bash
python -m pip install -e .
```

## Usage

```bash
watchllm-kernel --help
python -m watchllm_kernel --help
```

## Fixture corpus

Rule evidence fixtures live under `tests/fixtures/rules/`.

Each MVP rule category has a minimal `pass/` and `fail/` fixture set:

- `secrets`
- `forbidden_imports`
- `boundary`
- `auth_flow`

These fixtures are rule evidence examples and are used by rule-specific tests as each rule is implemented.

## Implemented rules

### Secret-literal rule

The secret-literal rule detects hardcoded credential patterns in assignment contexts and dangerous call contexts. It uses AST context to avoid flagging safe retrieval calls such as `process.env.STRIPE_SECRET` or `os.getenv("STRIPE_SECRET")`.

### Forbidden-import rule

The forbidden-import rule blocks dangerous imports such as `child_process` and disallowed relative traversal imports. It extracts ES module imports and CommonJS `require(...)` calls using AST traversal rather than raw text scanning.

### Boundary rule

The boundary rule checks AST-extracted import edges against a small declared boundary map. In the current policy, `auth` may import the public DB contract but must not import `db/internal` paths directly.

Circular dependency detection is explicitly deferred because Task 08 evaluates single-file import edges only, not a repository-wide import graph.

### Auth-flow rule

The auth-flow rule checks calls inside an exported `handler` function and requires an explicit auth guard before protected database operations such as `db.user.update(...)`.

Current Task 09 behaviour is intentionally narrow:

- mutation before auth returns `FAIL`
- auth before mutation returns `PASS`
- auth found only inside an ambiguous branch before mutation returns `INCONCLUSIVE`

Repository-wide control-flow analysis is not implemented yet.

## Decision engine

The decision engine runs a supplied ordered list of rules against one source buffer and reduces their rule results into one `KernelResult`.

In enforce mode, any rule failure produces `BLOCK`.

In shadow mode, rule failures are preserved in the result but the final decision remains `ALLOW`.

For Task 10, `INCONCLUSIVE` rule results are recorded but do not block.

## Benchmarks

Run the current Python kernel benchmark suite with:

```bash
python benchmarks/run_benchmarks.py --iterations 50 --warmup 5 --json
```

Benchmark baseline documentation lives in `docs/benchmarks/baseline.md`.

## Local violation reporting

Blocked evaluations are written locally as JSONL.

Default path:

```bash
.watchllm/logs/violations.jsonl
```

Override path:

```bash
WATCHLLM_LOG_PATH=/tmp/watchllm-violations.jsonl python -m watchllm_kernel evaluate path/to/file.ts --json
```

The reporting contract is documented in `docs/specs/reporting-contract.md`.

## Non‑goals (current state)

- No save-path editor integration yet
- No cloud dependency or network enforcement
