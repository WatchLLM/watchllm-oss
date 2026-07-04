# Daily Task Notes

## Date
2026-05-21

### Task
KERNEL-001 — Build repo skeleton

### Objective
Create the minimal repository layout for the kernel: package directory, CLI entrypoint, tests, and project manifest.

### Files Touched
- pyproject.toml
- src/watchllm_kernel/__init__.py
- src/watchllm_kernel/__main__.py
- src/watchllm_kernel/cli.py
- README.md
- tasks.md
- docs/README.md
- rules/README.md
- tests/test_cli.py
- daily_tasks_notes.md

### Changes Made
- Added `[tool.setuptools] package-dir` to pyproject.toml for explicit src layout.
- Created `src/watchllm_kernel/` package with `__init__.py`, `__main__.py`, and `cli.py`.
- Implemented minimal argparse CLI with `--version` and help.
- Added root README with installation and usage instructions.
- Created `tasks.md` with Task 01 status and gate description.
- Added placeholder READMEs for `docs/` and `rules/`.
- Added `tests/test_cli.py` using stdlib unittest and subprocess.
- Updated daily tasks notes with this entry.

### Architectural Reasoning
- Package under `src/` prevents accidental imports from repo root.
- CLI is independent of parser/rules so startup cannot break due to future incomplete modules.
- Using argparse and stdlib unittest avoids new dependencies in Task 01.
- Tracking `docs/` and `rules/` with README files rather than adding fake implementation.

### Alternatives Considered
- Placing package directly at repo root: rejected because it would allow accidental imports and complicate editable installs.
- Using pytest: rejected to keep Task 01 dependency‑free.

### Potential Failure Points
- Missing `[tool.setuptools] package-dir` can cause package discovery/install issues.
- Importing future parser/rule modules from `cli.py` would violate Task 01 and can break startup.
- Tests run before editable install may fail because `src/` is not on `PYTHONPATH`.
- Console script may not be available until after reinstalling with `pip install -e .`.

### Tests Added
- `test_module_help_exit_zero`
- `test_help_output_contains_watchllm`
- `test_import_cli_does_not_break`
- `test_main_help_returns_cleanly`

### Benchmarks
No benchmark added because no hot path exists yet; CLI startup only validated.

### Gate Result
PASS (expected after validation)

### Remaining Risks
- None for Task 01 scope.

### Notes For Next Task
- Next task: Task 02 — Define the core data model.
- Ensure editable install is performed before running tests.

---

## Date
2026-05-21

### Task
KERNEL-002 — Define the core data model

### Objective
Create the internal types for files, rules, violations, and decisions.

### Files Touched
- src/watchllm_kernel/models.py (new)
- tests/test_models.py (new)
- src/watchllm_kernel/__init__.py (updated)
- README.md (updated)
- tasks.md (updated)
- daily_tasks_notes.md (updated)

### Changes Made
- Added `src/watchllm_kernel/models.py` with dataclasses and enums for Decision, RuleDecision, Severity, SourceLocation, Violation, RuleResult, KernelResult, and an abstract Rule base class.
- Added `tests/test_models.py` covering enum values, dataclass defaults, violation creation, rule result aggregation, kernel result fields, and abstract rule evaluation.
- Updated `src/watchllm_kernel/__init__.py` to export key model symbols.
- Updated `README.md` to reflect Task 02 completion.
- Updated `tasks.md` to mark Task 02 as complete and describe its gate.
- Updated daily tasks notes with this entry.

### Architectural Reasoning
- Using dataclasses keeps the model lightweight and serializable.
- Enums enforce a closed set of decisions and severities, preventing accidental invalid states.
- The abstract Rule class defines the contract that all future rules must implement, ensuring consistency.
- No dependency on parser or editor code; models are pure data.

### Alternatives Considered
- Using Pydantic: rejected to keep dependencies minimal in the kernel phase.
- Embedding rule logic in models: rejected to maintain separation of concerns.

### Potential Failure Points
- If future rules do not implement `evaluate()`, they will raise NotImplementedError at runtime.
- Serialization of dataclasses may require custom JSON handling later; not needed now.

### Tests Added
- `test_decision_enum_values`
- `test_rule_decision_enum_values`
- `test_severity_enum_values`
- `test_source_location_defaults`
- `test_source_location_full`
- `test_violation_creation`
- `test_violation_defaults`
- `test_rule_result_pass`
- `test_rule_result_fail_with_violations`
- `test_kernel_result_allow`
- `test_kernel_result_block`
- `test_rule_abstract_evaluate_raises`
- `test_rule_attributes`

### Benchmarks
No benchmarks added; models are pure data and have no measurable hot path.

### Gate Result
PASS (expected after validation)

### Remaining Risks
- None for Task 02 scope.

### Notes For Next Task
- Next task: Task 03 — Implement source loading and parse entrypoint.
- Ensure editable install is performed before running tests.

---

## Date
2026-05-25

### Task
KERNEL-005 — Build fixture corpus

### Objective
Create minimal pass/fail fixtures for MVP rule categories and add automatic fixture discovery tests.

### Files Touched
- tests/fixtures/rules/secrets/pass/env_stripe_secret.ts
- tests/fixtures/rules/secrets/fail/hardcoded_stripe_secret.ts
- tests/fixtures/rules/forbidden_imports/pass/safe_local_import.js
- tests/fixtures/rules/forbidden_imports/fail/child_process_import.js
- tests/fixtures/rules/boundary/pass/auth_imports_public_contract.ts
- tests/fixtures/rules/boundary/fail/auth_imports_db_internal.ts
- tests/fixtures/rules/auth_flow/pass/auth_before_mutation.ts
- tests/fixtures/rules/auth_flow/fail/mutation_before_auth.ts
- tests/test_fixture_corpus.py
- README.md
- tasks.md
- daily_tasks_notes.md

### Changes Made
- Added readable minimal JS/TS fixtures for secrets, forbidden imports, boundary checks, and auth-flow checks.
- Added one pass and one fail fixture for each MVP rule category.
- Added automatic fixture discovery tests using stdlib unittest.
- Kept fixtures independent from parser, rule engine, CLI, and editor integration.

### Architectural Reasoning
- Fixtures are treated as rule evidence before rule implementation.
- Pass/fail directory layout keeps expected outcomes explicit.
- Automatic discovery prevents future fixture drift and supports later golden tests.
- Tests validate corpus structure without prematurely implementing rule semantics.

### Alternatives Considered
- Using a manifest file: rejected for now because deterministic filesystem discovery is enough.
- Parsing fixtures in this task: rejected because Task 05 is corpus construction, not parser validation.
- Adding many adversarial fixtures now: rejected to keep the corpus minimal and readable.

### Potential Failure Points
- Future rule implementations may interpret these fixtures differently unless rule semantics are documented clearly.
- Fixture names and layout become part of testing convention and should not be changed casually.
- Minimal fixtures may need expansion when false-positive and bypass cases are introduced.

### Tests Added
- Fixture category directory existence test.
- Pass/fail fixture presence test for each MVP rule category.
- Fixture readability and size test.
- Deterministic automatic discovery test.

### Benchmarks
No benchmark added. Fixture loading is lightweight and not part of the save-path hot path.

### Gate Result
PASS after validation

### Remaining Risks
- No real rule behaviour is proven yet; fixtures only provide evidence examples.
- Regression and adversarial fixture sets are deferred.

### Notes For Next Task
- Next task: Task 06 — Implement the secret-literal rule using these fixtures.

---

## Date
2026-05-28

### Task
KERNEL-008 — Implement the boundary rule

### Objective
Add deterministic boundary enforcement for declared service/module import relationships.

### Files Touched
- src/watchllm_kernel/rules/boundary.py
- tests/test_boundary_rule.py
- README.md
- tasks.md
- daily_tasks_notes.md

### Changes Made
- Added boundary rule using the existing core rule result model.
- Added import edge extraction from AST-derived import paths.
- Added source module inference from file paths.
- Added target classification for DB public/internal imports.
- Added default boundary map blocking `auth` from importing `db/internal`.
- Explicitly deferred circular dependency detection for repository-wide graph analysis.
- Added tests for failing internal DB imports, passing public DB imports, import edge extraction, and circular dependency exclusion.

### Architectural Reasoning
- Boundary logic is isolated from CLI, editor integration, and decision aggregation.
- The rule reuses AST import extraction from the forbidden-import rule instead of scanning raw text.
- Boundary checks are deterministic and do not resolve paths against the filesystem.
- Circular dependency detection is deferred because it requires a repository-wide graph, not a single-file rule.

### Alternatives Considered
- Filesystem path resolution: rejected because save-path enforcement must stay deterministic and local-input based.
- Repository-wide cycle detection in this task: rejected because Task 08 only requires boundary rule enforcement against fixtures.
- Raw regex import scanning: rejected because the kernel rules should use AST-derived import evidence.

### Potential Failure Points
- Source module inference is intentionally minimal and depends on file path conventions.
- Boundary map is hardcoded until policy configuration is introduced.
- Only DB public/internal surfaces are classified currently.
- Circular dependency detection is not implemented.

### Tests Added
- Source module inference test.
- Import target classification test.
- Import edge extraction test.
- Disallowed boundary fixture failure test.
- Allowed boundary fixture pass test.
- Boundary violation helper test.
- Explicit circular dependency exclusion test.

### Benchmarks
No benchmark added. Rule benchmarking belongs to the dedicated benchmark task.

### Gate Result
PASS after validation

### Remaining Risks
- Repository-wide import graph and circular dependency checks are deferred.
- Boundary policy versioning/configuration is not implemented yet.

### Notes For Next Task
- Next rule work should continue with the remaining MVP rules without coupling them to CLI or editor code.

---

## Date
2026-05-29

### Task
KERNEL-009 — Implement the auth-flow rule

### Objective
Add deterministic flow-sensitive auth-before-mutation checks within handler scope.

### Files Touched
- src/watchllm_kernel/rules/auth_flow.py
- tests/test_auth_flow_rule.py
- README.md
- tasks.md
- daily_tasks_notes.md

### Changes Made
- Added auth-flow rule using the existing core `RuleResult` model.
- Added AST-based call extraction inside `handler` functions.
- Added protected database operation detection.
- Added explicit auth guard detection.
- Added ordered evaluation so mutation before auth fails and auth before mutation passes.
- Added explicit `INCONCLUSIVE` handling for auth guards inside ambiguous branch/control-flow contexts.
- Added tests for fixture pass/fail behaviour and documented inconclusive behaviour.

### Architectural Reasoning
- Rule logic is isolated from CLI, editor integration, and decision aggregation.
- AST call extraction avoids matching comments or unrelated string literals.
- Task 09 keeps analysis intentionally local to handler scope.
- Ambiguous branch handling returns `INCONCLUSIVE` instead of pretending to prove path safety.

### Alternatives Considered
- Full path-sensitive control-flow analysis: rejected because it exceeds Task 09 scope.
- Regex-based call ordering: rejected because the kernel rules should use AST evidence.
- Treating ambiguous branch auth as pass: rejected because it can allow unguarded paths.

### Potential Failure Points
- Handler detection currently recognises only named `handler` function declarations.
- Protected operation detection is based on configured DB method names.
- Guard detection recognises explicit known guard calls only.
- Full path-sensitive analysis is deferred.

### Tests Added
- Protected operation helper test.
- Auth guard helper test.
- Call-event extraction test.
- Mutation-before-auth fail fixture test.
- Auth-before-mutation pass fixture test.
- Ambiguous auth branch inconclusive test.
- Inconclusive policy documentation test.
- Non-handler source pass test.

### Benchmarks
No benchmark added. Rule benchmarking belongs to the dedicated benchmark task.

### Gate Result
PASS

### Remaining Risks
- Path-sensitive control flow is not implemented.
- Handler framework detection is intentionally minimal.
- Policy configuration is hardcoded for now.

### Notes For Next Task
- Next work should combine implemented rules only when the decision engine task begins.

---

## Date
2026-05-30

### Task
KERNEL-010 — Build the decision engine

### Objective
Combine rule results into a deterministic kernel-level decision.

### Files Touched
- src/watchllm_kernel/engine.py
- tests/test_engine.py
- README.md
- tasks.md
- daily_tasks_notes.md

### Changes Made
- Added a generic ordered rule runner.
- Added violation aggregation across rule results.
- Added enforce/shadow decision reduction.
- Added `evaluate_source` returning a coherent `KernelResult`.
- Added tests for multiple rule execution, enforce blocking, shadow allowing, inconclusive handling, and metadata preservation.

### Architectural Reasoning
- The engine is isolated from CLI and editor integration.
- Rules are injected explicitly to keep evaluation deterministic and testable.
- Enforce/shadow semantics are centralised before adding CLI wiring.
- `INCONCLUSIVE` is recorded but non-blocking for Task 10.

### Alternatives Considered
- Instantiating default rules inside the engine: rejected because rule registry/policy loading is not defined yet.
- Catching rule exceptions in the engine: rejected for Task 10 because failure semantics need a dedicated policy.
- Wiring CLI in the same task: rejected because Task 11 owns CLI interface and JSON contract.

### Potential Failure Points
- Later policy may require `INCONCLUSIVE` to block or produce a distinct top-level state.
- Rule ordering is caller-controlled and must remain deterministic.
- Exception handling policy is not implemented yet.

### Tests Added
- Multiple rules run on one source test.
- Enforce blocks on any failure test.
- Enforce allows all-pass test.
- Shadow allows with failed rule test.
- Violation aggregation order test.
- Inconclusive non-blocking policy test.
- Invalid mode test.
- Kernel result metadata test.

### Benchmarks
No benchmark added. Engine benchmarking belongs to the dedicated benchmark task.

### Gate Result
PASS after validation

### Remaining Risks
- No CLI invokes the engine yet.
- No default rule registry exists yet.
- Exception/fail-safe policy is deferred.

### Notes For Next Task
- Task 11 should wire CLI flags, stdin/file loading, mode selection, JSON output, and exit codes to this engine.

---

## Date
2026-05-31

### Task
KERNEL-011 — Build CLI interface

### Objective
Wire the decision engine to a CLI with stdin/file input, enforce/shadow modes, JSON output, and correct exit codes.

### Files Touched
- src/watchllm_kernel/cli.py
- src/watchllm_kernel/rules/forbidden_imports.py (new)
- tests/test_cli.py
- tasks.md
- daily_tasks_notes.md

### Changes Made
- Added `evaluate` subcommand to CLI with `--stdin`, file path, `--language`, `--mode`, and `--json` flags.
- Implemented `build_default_rules()` that optionally includes the secret-literal rule and always includes forbidden-import, boundary, and auth-flow rules.
- Added JSON serialisation helper `_to_jsonable` that converts dataclasses and enums to primitives.
- Added language inference from file extension.
- Added exit code 1 when decision is BLOCK, 0 otherwise.
- Created `src/watchllm_kernel/rules/forbidden_imports.py` with AST-based import extraction and `ForbiddenImportRule`.
- Added five CLI evaluation tests: secret pass, secret fail, forbidden import fail, shadow mode allows failing fixture, and stdin evaluation.

### Architectural Reasoning
- CLI is a thin wrapper around the engine; all enforcement logic stays in the engine and rules.
- JSON output uses a generic dataclass/enum converter to avoid coupling to specific model shapes.
- The secret-literal rule is optional to keep the CLI working even if that rule is not yet implemented.
- Forbidden-import rule was added because the CLI default wiring imports it and the tests rely on `child_process` being blocked.

### Alternatives Considered
- Hardcoding rule list without optional secret rule: rejected because it would break when the secret rule module is missing.
- Using a separate JSON schema library: rejected to keep dependencies minimal.

### Potential Failure Points
- If `ForbiddenImportRule` is not importable the CLI will fail at startup.
- JSON serialisation may need updating if model fields change.
- Language inference is based on file extension only; explicit `--language` flag is available as override.

### Tests Added
- `test_evaluate_secret_pass_returns_allow`
- `test_evaluate_secret_fail_returns_block`
- `test_evaluate_forbidden_import_fail_returns_block`
- `test_evaluate_shadow_mode_allows_failing_fixture`
- `test_evaluate_stdin_works`

### Benchmarks
No benchmark added. CLI benchmarking belongs to the dedicated benchmark task.

### Gate Result
PASS after validation

### Remaining Risks
- No editor integration yet.
- No remote policy loading.
- Save-path interception is not implemented.

### Notes For Next Task
- Task 12 — Add tests for end-to-end behaviour.

---

## Date
2026-06-01

### Task
KERNEL-012 — Add tests for end-to-end behaviour

### Objective
Prove the whole kernel works as one system with deterministic regression tests.

### Files Touched
- tests/test_e2e.py
- src/watchllm_kernel/rules/secrets.py (new)
- README.md
- tasks.md
- daily_tasks_notes.md

### Changes Made
- Added end-to-end test suite covering all pass/fail fixtures in enforce and shadow modes.
- Added deterministic regression test that compares two runs of all fixtures.
- Added CLI stdin save-path simulation test.
- Added CLI JSON output stability test.
- Created `src/watchllm_kernel/rules/secrets.py` with AST-based secret-literal rule.
- Updated README to reflect Task 12 completion.
- Updated tasks.md with Task 12 section and marked Task 10 as Complete.
- Updated daily tasks notes with this entry.

### Architectural Reasoning
- End-to-end tests use the same `build_default_rules()` and `evaluate_source()` as the CLI, ensuring the whole pipeline is exercised.
- Regression determinism test runs the full fixture set twice and compares snapshots, proving no hidden state or randomness.
- The secret-literal rule was added because the E2E tests require the secret fail fixture to block in enforce mode.
- CLI simulation tests use subprocess to validate the actual command-line contract.

### Alternatives Considered
- Skipping the secret fixture in E2E tests: rejected because Task 12 requires all fail fixtures to block.
- Using a separate test runner: rejected to keep the test suite dependency-free.

### Potential Failure Points
- If the secret-literal rule module is missing, the E2E tests will fail because the secret fail fixture will not block.
- Fixture discovery depends on the filesystem layout; moving fixtures would break tests.
- CLI subprocess tests require the package to be installed in editable mode.

### Tests Added
- `test_passing_fixtures_allow_in_enforce_mode`
- `test_failing_fixtures_block_in_enforce_mode`
- `test_shadow_mode_does_not_block_failing_fixtures`
- `test_regression_results_are_deterministic_across_runs`
- `test_cli_stdin_save_path_simulation_blocks_unsafe_source`
- `test_cli_json_output_is_valid_and_stable`

### Benchmarks
No benchmark added. End-to-end benchmarking belongs to the dedicated benchmark task.

### Gate Result
PASS after validation

### Remaining Risks
- No editor integration yet.
- No remote policy loading.
- Save-path interception is not implemented.

### Notes For Next Task
- Task 13 — Add performance benchmarks.

### State Snapshot
- Added `docs/CODEBASE_STATE.md` to preserve current task/implementation state for future agent continuity.

---

## Date
2026-06-02

### Task
KERNEL-DOCS — Reconcile completed task ledger for Tasks 03, 04, and 07

### Objective
Backfill missing task documentation for already implemented parser/source-loading and forbidden-import work before proceeding to Task 13.

### Files Touched
- tasks.md
- docs/CODEBASE_STATE.md
- README.md
- daily_tasks_notes.md

### Changes Made
- Added missing Task 03 completion section to `tasks.md`.
- Added missing Task 04 completion section to `tasks.md`.
- Added missing Task 07 completion section to `tasks.md`.
- Added parser module status to `docs/CODEBASE_STATE.md`.
- Updated README current status and forbidden-import rule documentation.

### Architectural Reasoning
The implementation had advanced beyond the task ledger. This reconciliation keeps the project history deterministic and prevents future agents from thinking parser and forbidden-import work are incomplete.

### Alternatives Considered
- Reordering implementation history: rejected because it would fabricate chronology.
- Redoing implemented tasks: rejected because tests already cover the contracts.

### Potential Failure Points
- Historical dates remain approximate because the ledger was backfilled after implementation.
- Future contributors may still need to inspect tests for exact implementation coverage.

### Tests Added
None. Documentation-only reconciliation.

### Benchmarks
None.

### Gate Result
PASS after validation

### Remaining Risks
- The task ledger is now structurally correct, but historical implementation order was not perfectly recorded at the time.

### Notes For Next Task
- Proceed to Task 13 — Add performance benchmarks.

---

## Date
2026-06-02

### Task
KERNEL-013 — Add performance benchmarks

### Objective
Add measurable parser, rule evaluation, and end-to-end benchmark coverage for the current Python kernel.

### Files Touched
- benchmarks/run_benchmarks.py
- tests/test_benchmarks.py
- docs/benchmarks/baseline.md
- docs/CODEBASE_STATE.md
- README.md
- tasks.md
- daily_tasks_notes.md

### Changes Made
- Added benchmark runner with deterministic fixture discovery.
- Added JSON benchmark output schema.
- Added subprocess tests for benchmark command and output file writing.
- Recorded baseline benchmark documentation.
- Updated task and codebase state documentation.

### Architectural Reasoning
Benchmarks are measurement-only and preserve deterministic local enforcement. No rule semantics, parser contracts, engine contracts, or CLI enforcement contracts were changed.

### Alternatives Considered
- Adding pytest-benchmark: rejected to avoid new dependencies.
- Enforcing budgets immediately: rejected because the Python kernel is the baseline before Rust/Wasm optimisation.

### Potential Failure Points
- Timings vary by machine.
- Current rule evaluation may include rule-local parsing overhead.
- Fixture corpus is still small.

### Tests Added
- tests/test_benchmarks.py

### Benchmarks
- Parser latency recorded.
- Rule evaluation latency recorded.
- End-to-end latency recorded.

### Gate Result
PASS after validation

### Remaining Risks
- Benchmarks are not yet broad enough to represent large repositories.
- Budgets are informational only.

### Notes For Next Task
- Task 14 should add local logging and violation reporting.

---

## Date
2026-06-02

### Task
KERNEL-014 — Add local logging and violation reporting

### Objective
Add local blocked-event reporting so violations are visible without any cloud dependency.

### Files Touched
- src/watchllm_kernel/reporting.py
- src/watchllm_kernel/cli.py
- tests/test_reporting.py
- tests/test_cli.py
- docs/specs/reporting-contract.md
- docs/CODEBASE_STATE.md
- README.md
- tasks.md
- daily_tasks_notes.md

### Changes Made
- Added local violation report schema.
- Added JSONL blocked-event logging.
- Added human-readable violation report formatting.
- Wired CLI blocked evaluations to local logging.
- Added reporting unit tests and CLI logging integration test.
- Documented the reporting contract.

### Architectural Reasoning
Reporting is local-only and separated from enforcement. Logging records deterministic rule outcomes after evaluation and does not participate in allow/block decisions.

### Alternatives Considered
- Cloud telemetry: rejected because Task 14 is local reporting only.
- Logging from inside rules: rejected because rules should only evaluate and return results.
- Changing engine decisions to include reporting metadata: rejected to preserve Task 10 engine contract.

### Potential Failure Points
- Log path may be unwritable on restricted filesystems.
- Parse status is currently recorded as `not_recorded` because parsing is still rule-local.
- Timestamps make log entries non-identical across runs, though decisions remain deterministic.

### Tests Added
- tests/test_reporting.py
- CLI blocked-event logging test in tests/test_cli.py

### Benchmarks
No benchmark changes. Reporting is outside the hot benchmark path for Task 14.

### Gate Result
PASS after validation

### Remaining Risks
- Logging failures are not yet covered by an explicit fail-open/fail-closed policy.
- Central parse status should be improved after parser pipeline consolidation.

### Notes For Next Task
- Task 15 should stabilise the CLI/editor integration contract.

---

## Date
2026-06-02

### Task
KERNEL-QA-001 — Code quality refactor: eliminate duplication, single-parse, fix denylist, expand handler detection

### Objective
Address seven code quality issues identified during manual audit:
1. Massive code duplication across rule files (_make_parser, _node_text, _location_from_node, _wrap_language)
2. parser.py abstraction was never integrated — all rules bypassed it
3. Forbidden import denylist was too aggressive (blocked http, path, fs, stream, etc.)
4. Auth-flow handler detection was too narrow (only named `function handler()`)
5. Boundary rule lacked `__init__.py` for the rules package
6. secrets.py recreated its own parser independently
7. No single-parse: every rule parsed source independently

### Files Touched
- src/watchllm_kernel/rules/__init__.py (new)
- src/watchllm_kernel/rules/_ast_utils.py (new)
- src/watchllm_kernel/models.py (modified)
- src/watchllm_kernel/engine.py (modified)
- src/watchllm_kernel/rules/secrets.py (rewritten)
- src/watchllm_kernel/rules/forbidden_imports.py (rewritten)
- src/watchllm_kernel/rules/auth_flow.py (rewritten)
- src/watchllm_kernel/rules/boundary.py (rewritten)
- tests/test_engine.py (modified)
- tests/test_forbidden_import_rule.py (modified)
- daily_tasks_notes.md (updated)

### Changes Made

#### New: `rules/__init__.py`
- Created proper package init with public exports for all four rules.
- Centralises the import surface for consumers.

#### New: `rules/_ast_utils.py`
- Extracted shared helpers: `node_text`, `location_from_node`, `strip_quotes`, `infer_language_from_path`, `ensure_parse_result`.
- `ensure_parse_result()` is the key function: accepts an optional pre-parsed `ParseResult` and returns it directly if available, or calls `parser.parse_source()` if not. This is the mechanism that enables single-parse.
- All four rules now import from `_ast_utils` instead of maintaining their own copies.

#### Modified: `models.py`
- Extended `Rule.evaluate()` signature with an optional `parse_result: Optional[ParseResult]` parameter.
- Used `TYPE_CHECKING` import guard to avoid circular import with `parser.py`.
- Backward-compatible: existing calls without `parse_result` still work.

#### Modified: `engine.py`
- Engine now calls `parse_source()` once and passes the `ParseResult` to every rule via the new parameter.
- Infers language from file_path when not explicitly provided, ensuring `KernelResult.language` is always populated.
- This eliminates 4× redundant tree-sitter parsing per evaluation.

#### Rewritten: `secrets.py`
- Removed 35+ lines of duplicate tree-sitter boilerplate (_wrap_language, _make_parser, _node_text, _location_from_node).
- Now imports from `_ast_utils` and accepts `parse_result` from the engine.
- No logic changes to the rule itself — same patterns, same AST context checks.

#### Rewritten: `forbidden_imports.py`
- Removed duplicate tree-sitter boilerplate.
- **Tightened default denylist** from 21 modules to 2 (child_process, vm — the only ones that enable arbitrary code execution).
- Added `ELEVATED_RISK_MODULES` frozenset (fs, os, net, tls, etc.) for deployments that want stricter enforcement — these can be merged into `forbidden_modules` via the constructor.
- Added `extract_import_paths_from_tree()` that works directly on AST nodes without re-parsing.
- `extract_import_paths()` now accepts `parse_result` to avoid redundant parsing.
- Kept the `allowed_relative_prefixes` allowlist from the previous bug fix.

#### Rewritten: `auth_flow.py`
- Removed duplicate tree-sitter boilerplate.
- **Expanded handler detection**: now recognises three handler patterns:
  - Named function declarations: `function handler() { ... }`
  - Arrow functions: `const handler = async (req) => { ... }`
  - Function expressions: `const handleRequest = function(req) { ... }`
- Added `HANDLER_NAMES` constant: `handler`, `handleRequest`, `requestHandler`.
- Added `_is_handler_variable()` helper for arrow/expression detection.
- Cleaner walk architecture: `_walk()` finds handler scopes, `_walk_handler_body()` collects events inside them. Non-handler function declarations are still skipped entirely.
- Accepts `parse_result` from the engine.

#### Rewritten: `boundary.py`
- Accepts `parse_result` and passes it through to `extract_import_paths`, so the boundary rule benefits from single-parse.
- No logic changes to boundary detection itself.

#### Modified: `tests/test_engine.py`
- Updated mock rule `evaluate()` signatures to accept `**kwargs` for forward-compatibility with the new `parse_result` parameter.

#### Modified: `tests/test_forbidden_import_rule.py`
- Updated `test_multiple_forbidden_imports_fails` to use `vm` instead of `fs` since `fs` is no longer in the default denylist.

### Architectural Reasoning
- The central design principle: **parse once, evaluate many**. The engine is the single owner of parsing, and rules receive a pre-parsed tree. This matches the kernel's performance goals (< 10ms latency budget).
- `_ast_utils.py` follows the "shared utility layer" pattern. Rules import from it; it imports from `parser.py`. No rule imports `tree_sitter` directly anymore.
- The `ensure_parse_result()` fallback means rules still work standalone (e.g. in unit tests) when called without a `ParseResult` — backward compatibility is preserved.
- The denylist tightening is intentional: blocking `path`, `http`, `stream` etc. by default would make the kernel unusable on any real Node.js project. The `ELEVATED_RISK_MODULES` set gives operators the knobs to tighten enforcement per-deployment.
- Handler detection expansion stays conservative: only explicitly named handler variables are recognised. Framework-specific detection (Express routes, Next.js API routes) is deferred to a dedicated rule or configuration.

### Alternatives Considered
- Passing the raw tree-sitter Tree instead of ParseResult: rejected because ParseResult carries source bytes and language metadata that rules need.
- Moving all AST helpers into parser.py: rejected because rule-specific helpers (strip_quotes, safe-retrieval detection) don't belong in the parser layer.
- Making handler detection config-driven: deferred because the current set covers the most common patterns without over-engineering.
- Removing ELEVATED_RISK_MODULES: rejected because operators need a documented set they can opt into.

### Potential Failure Points
- Rules that override `evaluate()` without `**kwargs` or `parse_result` will break when the engine passes the new parameter. Mitigated by updating all existing rules and test stubs.
- The `infer_language_from_path()` fallback defaults to JavaScript — TypeScript files without a `.ts`/`.tsx` extension won't parse correctly. This matches prior behaviour.
- Arrow function handler detection only works for `variable_declarator` patterns. Immediately-invoked or passed-as-argument handlers are not detected.

### Tests Added
- No new test files added.
- All existing 92 tests pass (including 20 E2E subtests).
- Mock rule stubs in `test_engine.py` updated for new interface.
- `test_forbidden_import_rule.py` updated for tightened denylist.

### Benchmarks
- Benchmark runner (`benchmarks/run_benchmarks.py`) already uses `parse_source` from `parser.py` and benefits from the tree-sitter v0.25 fix applied in the previous session.
- No benchmark schema changes.

### Gate Result
PASS — 92 tests pass, 0 failures, 20 subtests pass.

### Remaining Risks
- Framework-specific handler detection (Express, Next.js) is not implemented.
- Boundary map is still hardcoded as a default; CLI flag for config loading is not yet available.
- `ELEVATED_RISK_MODULES` is documented but has no CLI toggle yet.
- `parse_status` in reporting is still `not_recorded` — could now be improved since parsing is centralised.

### Notes For Next Task
- Parser pipeline is now consolidated. Reporting `parse_status` can be set to `"ok"` or `"error"` based on tree-sitter parse results.
- Consider adding a `--strict` CLI flag that merges `ELEVATED_RISK_MODULES` into the denylist.
- Handler detection can be extended with a `handler_names` constructor parameter for per-project customisation.
