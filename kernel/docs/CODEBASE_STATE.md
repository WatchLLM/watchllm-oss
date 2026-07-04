# WatchLLM Kernel — Codebase State Snapshot

## Purpose

This document captures the current state of the kernel implementation so that future agents and contributors can resume work without losing context. It is a living snapshot, not a replacement for the task list or daily notes.

## Current task

Task 15 — Wrap for editor integration readiness (Complete)

## Implemented modules

| Module | Status | Notes |
|--------|--------|-------|
| `src/watchllm_kernel/models.py` | Complete | Core data model (Decision, RuleResult, Violation, etc.) |
| `src/watchllm_kernel/engine.py` | Complete | Deterministic decision engine with enforce/shadow modes |
| `src/watchllm_kernel/cli.py` | Complete | CLI entrypoint with evaluate subcommand, JSON output |
| `src/watchllm_kernel/rules/secrets.py` | Complete | Secret-literal rule with AST context checks |
| `src/watchllm_kernel/rules/forbidden_imports.py` | Complete | Forbidden-import rule with AST-based import extraction |
| `src/watchllm_kernel/rules/boundary.py` | Complete | Boundary rule enforcing declared service/module boundaries |
| `src/watchllm_kernel/rules/auth_flow.py` | Complete | Auth-flow rule requiring auth before protected operations |
| `src/watchllm_kernel/parser.py` | Complete | Tree-sitter parser abstraction for JavaScript, TypeScript, and TSX |
| `benchmarks/run_benchmarks.py` | Complete | Parser, rule evaluation, and end-to-end benchmark runner |
| `src/watchllm_kernel/reporting.py` | Complete | Local violation report formatting and JSONL blocked-event logging |

## Fixture corpus

| Category | Pass fixtures | Fail fixtures |
|----------|---------------|---------------|
| secrets | `env_stripe_secret.ts` | `hardcoded_stripe_secret.ts` |
| forbidden_imports | `safe_local_import.js` | `child_process_import.js` |
| boundary | `auth_imports_public_contract.ts` | `auth_imports_db_internal.ts` |
| auth_flow | `auth_before_mutation.ts` | `mutation_before_auth.ts` |

## Test coverage

| Test file | Scope |
|-----------|-------|
| `tests/test_models.py` | Core data model unit tests |
| `tests/test_engine.py` | Decision engine unit tests |
| `tests/test_cli.py` | CLI integration tests |
| `tests/test_e2e.py` | End-to-end regression tests |
| `tests/test_fixture_corpus.py` | Fixture discovery and structure tests |
| `tests/test_secret_rule.py` | Secret-literal rule tests |
| `tests/test_forbidden_import_rule.py` | Forbidden-import rule tests |
| `tests/test_boundary_rule.py` | Boundary rule tests |
| `tests/test_auth_flow_rule.py` | Auth-flow rule tests |
| `tests/test_benchmarks.py` | Benchmark command and JSON schema tests |
| `tests/test_reporting.py` | Local violation report and JSONL logging tests |

## Known limitations

- No save-path editor integration yet
- No remote policy loading
- Circular dependency detection is explicitly deferred
- Full path-sensitive control-flow analysis is not implemented
- Handler detection is intentionally minimal (named `handler` functions only)
- Boundary map is hardcoded; no policy configuration file support yet
- Some early tasks were implemented before being fully recorded; Tasks 03, 04, and 07 have now been backfilled in `tasks.md`
- Benchmark budgets are informational only; enforcement is deferred until optimisation work matures
- Parse status in reports is currently `not_recorded` because parsing is still rule-local rather than centrally tracked

## Next task

All kernel MVP tasks (01–15) are complete. The next phase is editor integration and save-path interception.
