⇒ WatchLLM Kernel — 15-Day Prompt Pack

Copy **one full day block** below into your agent session. Each block uses the same template; only task, gate, and scope placeholders are filled from `internal_docs/IMPORTANT.md`.

**Repo:** `watchllm/kernel` (local: `d:\watchllm\kernel`)

---

⇒ Day 01 — Task 01: Build the repo skeleton

⇒ Task Instructions

Today's task:
**KERNEL Task 01 — Build the repo skeleton**

Create the minimal repository layout for the kernel in `watchllm/kernel`:

- `src/`
- `tests/`
- `docs/`
- `rules/`
- `pyproject.toml` or equivalent project manifest
- `README.md`
- `tasks.md`

Do not implement parser, rules, or enforcement yet. Do not copy archived `WATCHLLM-CORE`.

Today's gate:
- Chosen package entrypoint runs successfully (e.g. `python -m <package> --help` per project manifest).
- Repository installs cleanly in a fresh environment.
- No placeholder imports break startup.

> Scope Constraints

Only work on:
- Repository skeleton and project manifest (Task 01 only)
- `src/`, `tests/`, `docs/`, `rules/`, `pyproject.toml`, `tasks.md`, `README.md`
- Directory layout, packaging, and a runnable `--help` entrypoint — no rule or parser logic

Do NOT:
- refactor unrelated systems
- introduce speculative abstractions
- modify contracts outside task scope
- add dependencies without justification

> Required Outputs

You must:
- implement the task narrowly
- write/update tests
- update documentation if architecture changes
- update internal_docs/KERNEL_DAILY_TASKS_NOTES.md
- explain architectural decisions
- explain potential failure points
- explain benchmark/performance implications if relevant

> Validation Requirements

Before finishing:
- run tests
- verify gate behavior
- ensure deterministic output
- ensure no unrelated files changed

> Reporting Format

At the end, report:
1. Files changed
2. What changed
3. Why it changed
4. Potential failure points
5. Remaining risks
6. Benchmark impact
7. Gate status

---

⇒ Day 02 — Task 02: Define the core data model

⇒ Task Instructions

Today's task:
**KERNEL Task 02 — Define the core data model**

Create internal types for files, rules, violations, and decisions:

- Source file(s) for models/types
- Typed decision object
- Typed violation object
- Typed rule interface

Today's gate:
- Unit tests confirm the models serialize and deserialize correctly.
- A sample rule can return a structured decision object.
- No rule depends on editor-specific code.

> Scope Constraints

Only work on:
- Core data model layer (Task 02 only)
- Model/type modules under `src/` and corresponding unit tests under `tests/`
- Serialization, rule interface contract, and sample stub rule returning a structured decision

Do NOT:
- refactor unrelated systems
- introduce speculative abstractions
- modify contracts outside task scope
- add dependencies without justification

> Required Outputs

You must:
- implement the task narrowly
- write/update tests
- update documentation if architecture changes
- update internal_docs/KERNEL_DAILY_TASKS_NOTES.md
- explain architectural decisions
- explain potential failure points
- explain benchmark/performance implications if relevant

> Validation Requirements

Before finishing:
- run tests
- verify gate behavior
- ensure deterministic output
- ensure no unrelated files changed

> Reporting Format

At the end, report:
1. Files changed
2. What changed
3. Why it changed
4. Potential failure points
5. Remaining risks
6. Benchmark impact
7. Gate status

---

⇒ Day 03 — Task 03: Implement source loading and parse entrypoint

⇒ Task Instructions

Today's task:
**KERNEL Task 03 — Implement source loading and parse entrypoint**

Read source text and hand it to the parser pipeline:

- File reader / stdin reader
- Parse entrypoint
- Language detection or explicit language parameter handling

Today's gate:
- Test fixture source can be loaded from stdin and file path.
- Parser entrypoint returns a structured parse result.
- Invalid input is handled without crashing the process.

> Scope Constraints

Only work on:
- Source loading and parse entrypoint (Task 03 only)
- Loader modules, stdin/file path input, language parameter handling, structured parse result types
- Parser pipeline entry — not full JS/TS AST integration yet

Do NOT:
- refactor unrelated systems
- introduce speculative abstractions
- modify contracts outside task scope
- add dependencies without justification

> Required Outputs

You must:
- implement the task narrowly
- write/update tests
- update documentation if architecture changes
- update internal_docs/KERNEL_DAILY_TASKS_NOTES.md
- explain architectural decisions
- explain potential failure points
- explain benchmark/performance implications if relevant

> Validation Requirements

Before finishing:
- run tests
- verify gate behavior
- ensure deterministic output
- ensure no unrelated files changed

> Reporting Format

At the end, report:
1. Files changed
2. What changed
3. Why it changed
4. Potential failure points
5. Remaining risks
6. Benchmark impact
7. Gate status

---

⇒ Day 04 — Task 04: Integrate AST parsing for JS/TS

⇒ Task Instructions

Today's task:
**KERNEL Task 04 — Integrate AST parsing for JS/TS**

Parse JavaScript and TypeScript into AST form:

- JS parser integration
- TS parser integration
- AST normalization or wrapper

Today's gate:
- Known JS and TS fixtures parse successfully.
- Parse tree roots are visible to tests.
- Syntax-error fixtures do not crash the parser.

> Scope Constraints

Only work on:
- AST parsing layer for JavaScript and TypeScript (Task 04 only)
- Parser integration, AST wrapper/normalization, parser tests with JS/TS fixtures
- Structural parse only — no rule evaluation yet

Do NOT:
- refactor unrelated systems
- introduce speculative abstractions
- modify contracts outside task scope
- add dependencies without justification

> Required Outputs

You must:
- implement the task narrowly
- write/update tests
- update documentation if architecture changes
- update internal_docs/KERNEL_DAILY_TASKS_NOTES.md
- explain architectural decisions
- explain potential failure points
- explain benchmark/performance implications if relevant

> Validation Requirements

Before finishing:
- run tests
- verify gate behavior
- ensure deterministic output
- ensure no unrelated files changed

> Reporting Format

At the end, report:
1. Files changed
2. What changed
3. Why it changed
4. Potential failure points
5. Remaining risks
6. Benchmark impact
7. Gate status

---

⇒ Day 05 — Task 05: Build fixture corpus

⇒ Task Instructions

Today's task:
**KERNEL Task 05 — Build fixture corpus**

Create small, explicit examples for passing and failing cases:

- Positive and negative fixtures for secrets
- Positive and negative fixtures for forbidden imports
- Positive and negative fixtures for boundary violations
- Positive and negative fixtures for auth-flow checks

Today's gate:
- Each rule has at least one pass and one fail fixture.
- Fixtures are readable and minimal.
- Tests can load all fixtures automatically.

> Scope Constraints

Only work on:
- Fixture corpus (Task 05 only)
- `tests/fixtures/` or `fixtures/` pass/fail/regression layout per project convention
- Minimal JS/TS sample files and automatic fixture loading in tests

Do NOT:
- refactor unrelated systems
- introduce speculative abstractions
- modify contracts outside task scope
- add dependencies without justification

> Required Outputs

You must:
- implement the task narrowly
- write/update tests
- update documentation if architecture changes
- update internal_docs/KERNEL_DAILY_TASKS_NOTES.md
- explain architectural decisions
- explain potential failure points
- explain benchmark/performance implications if relevant

> Validation Requirements

Before finishing:
- run tests
- verify gate behavior
- ensure deterministic output
- ensure no unrelated files changed

> Reporting Format

At the end, report:
1. Files changed
2. What changed
3. Why it changed
4. Potential failure points
5. Remaining risks
6. Benchmark impact
7. Gate status

---

⇒ Day 06 — Task 06: Implement the secret-literal rule

⇒ Task Instructions

Today's task:
**KERNEL Task 06 — Implement the secret-literal rule**

Detect hardcoded secret patterns in structural context:

- Rule implementation
- AST context checks
- Safe retrieval allowance logic

Today's gate:
- Hardcoded secret fixtures fail.
- Env-var retrieval fixtures pass.
- Comment/string/mock false positives are not allowed to block.
- Unit tests cover at least 3 positive and 3 negative cases.

> Scope Constraints

Only work on:
- Secret-literal rule (Task 06 only)
- Rule module under `src/` or `rules/`, AST context checks, safe-function filtering (`process.env`, `os.getenv`, etc.)
- Tests against Task 05 secret fixtures only

Do NOT:
- refactor unrelated systems
- introduce speculative abstractions
- modify contracts outside task scope
- add dependencies without justification

> Required Outputs

You must:
- implement the task narrowly
- write/update tests
- update documentation if architecture changes
- update internal_docs/KERNEL_DAILY_TASKS_NOTES.md
- explain architectural decisions
- explain potential failure points
- explain benchmark/performance implications if relevant

> Validation Requirements

Before finishing:
- run tests
- verify gate behavior
- ensure deterministic output
- ensure no unrelated files changed

> Reporting Format

At the end, report:
1. Files changed
2. What changed
3. Why it changed
4. Potential failure points
5. Remaining risks
6. Benchmark impact
7. Gate status

---

⇒ Day 07 — Task 07: Implement the forbidden-import rule

⇒ Task Instructions

Today's task:
**KERNEL Task 07 — Implement the forbidden-import rule**

Block disallowed imports and unsafe module access paths:

- Rule implementation
- Allowlist/denylist structure
- Path normalization logic

Today's gate:
- Forbidden imports fail.
- Allowed internal imports pass.
- Relative traversal violations are detected.
- Tests prove no accidental blocking of safe imports.

> Scope Constraints

Only work on:
- Forbidden-import rule (Task 07 only)
- Denylist/allowlist config, import path normalization, rule evaluation against import AST nodes
- Tests against Task 05 forbidden-import fixtures only

Do NOT:
- refactor unrelated systems
- introduce speculative abstractions
- modify contracts outside task scope
- add dependencies without justification

> Required Outputs

You must:
- implement the task narrowly
- write/update tests
- update documentation if architecture changes
- update internal_docs/KERNEL_DAILY_TASKS_NOTES.md
- explain architectural decisions
- explain potential failure points
- explain benchmark/performance implications if relevant

> Validation Requirements

Before finishing:
- run tests
- verify gate behavior
- ensure deterministic output
- ensure no unrelated files changed

> Reporting Format

At the end, report:
1. Files changed
2. What changed
3. Why it changed
4. Potential failure points
5. Remaining risks
6. Benchmark impact
7. Gate status

---

⇒ Day 08 — Task 08: Implement the boundary rule

⇒ Task Instructions

Today's task:
**KERNEL Task 08 — Implement the boundary rule**

Enforce declared service/module boundaries:

- Import graph extraction
- Boundary map
- Boundary enforcement logic

Today's gate:
- Disallowed cross-boundary edges fail.
- Allowed edges pass.
- Circular dependency case is detected or explicitly excluded with a stated rule.

> Scope Constraints

Only work on:
- Boundary rule (Task 08 only)
- Import graph extraction, boundary map configuration, cross-boundary enforcement logic
- Tests against Task 05 boundary fixtures only

Do NOT:
- refactor unrelated systems
- introduce speculative abstractions
- modify contracts outside task scope
- add dependencies without justification

> Required Outputs

You must:
- implement the task narrowly
- write/update tests
- update documentation if architecture changes
- update internal_docs/KERNEL_DAILY_TASKS_NOTES.md
- explain architectural decisions
- explain potential failure points
- explain benchmark/performance implications if relevant

> Validation Requirements

Before finishing:
- run tests
- verify gate behavior
- ensure deterministic output
- ensure no unrelated files changed

> Reporting Format

At the end, report:
1. Files changed
2. What changed
3. Why it changed
4. Potential failure points
5. Remaining risks
6. Benchmark impact
7. Gate status

---

⇒ Day 09 — Task 09: Implement the auth-flow rule

⇒ Task Instructions

Today's task:
**KERNEL Task 09 — Implement the auth-flow rule**

Require auth verification before protected operations:

- Flow-sensitive call analysis
- Protected operation detection
- Guard-call detection

Today's gate:
- A handler that mutates data before auth fails.
- A handler that authenticates first passes.
- A handler with ambiguous order is either flagged or marked inconclusive by spec.

> Scope Constraints

Only work on:
- Auth-flow rule (Task 09 only)
- Flow-sensitive analysis within handler scope, protected-operation detection, guard-call detection
- Tests against Task 05 auth-flow fixtures; document inconclusive behavior explicitly

Do NOT:
- refactor unrelated systems
- introduce speculative abstractions
- modify contracts outside task scope
- add dependencies without justification

> Required Outputs

You must:
- implement the task narrowly
- write/update tests
- update documentation if architecture changes
- update internal_docs/KERNEL_DAILY_TASKS_NOTES.md
- explain architectural decisions
- explain potential failure points
- explain benchmark/performance implications if relevant

> Validation Requirements

Before finishing:
- run tests
- verify gate behavior
- ensure deterministic output
- ensure no unrelated files changed

> Reporting Format

At the end, report:
1. Files changed
2. What changed
3. Why it changed
4. Potential failure points
5. Remaining risks
6. Benchmark impact
7. Gate status

---

⇒ Day 10 — Task 10: Build the decision engine

⇒ Task Instructions

Today's task:
**KERNEL Task 10 — Build the decision engine**

Combine rules into a single deterministic evaluator:

- Rule runner
- Aggregator
- Decision reduction logic

Today's gate:
- Multiple rules can run on one source file.
- The engine returns a single coherent decision object.
- Blocking any one rule in enforce mode blocks the save.

> Scope Constraints

Only work on:
- Decision engine (Task 10 only)
- Rule runner, violation aggregator, enforce/shadow decision reduction
- Wiring Tasks 06–09 rules into one deterministic evaluation path

Do NOT:
- refactor unrelated systems
- introduce speculative abstractions
- modify contracts outside task scope
- add dependencies without justification

> Required Outputs

You must:
- implement the task narrowly
- write/update tests
- update documentation if architecture changes
- update internal_docs/KERNEL_DAILY_TASKS_NOTES.md
- explain architectural decisions
- explain potential failure points
- explain benchmark/performance implications if relevant

> Validation Requirements

Before finishing:
- run tests
- verify gate behavior
- ensure deterministic output
- ensure no unrelated files changed

> Reporting Format

At the end, report:
1. Files changed
2. What changed
3. Why it changed
4. Potential failure points
5. Remaining risks
6. Benchmark impact
7. Gate status

---

⇒ Day 11 — Task 11: Build CLI interface

⇒ Task Instructions

Today's task:
**KERNEL Task 11 — Build CLI interface**

Provide a terminal entrypoint for the kernel:

- `--stdin` support
- File path support
- Language flag support
- Enforce/shadow mode switch
- Machine-readable output

Today's gate:
- `--help` works.
- A sample file can be evaluated from stdin.
- Exit codes are correct.
- JSON output is valid and stable.

> Scope Constraints

Only work on:
- CLI interface (Task 11 only)
- Terminal entrypoint, flags (`--stdin`, file path, language, enforce/shadow), exit codes, JSON output contract
- CLI invokes decision engine — no editor integration yet

Do NOT:
- refactor unrelated systems
- introduce speculative abstractions
- modify contracts outside task scope
- add dependencies without justification

> Required Outputs

You must:
- implement the task narrowly
- write/update tests
- update documentation if architecture changes
- update internal_docs/KERNEL_DAILY_TASKS_NOTES.md
- explain architectural decisions
- explain potential failure points
- explain benchmark/performance implications if relevant

> Validation Requirements

Before finishing:
- run tests
- verify gate behavior
- ensure deterministic output
- ensure no unrelated files changed

> Reporting Format

At the end, report:
1. Files changed
2. What changed
3. Why it changed
4. Potential failure points
5. Remaining risks
6. Benchmark impact
7. Gate status

---

⇒ Day 12 — Task 12: Add tests for end-to-end behavior

⇒ Task Instructions

Today's task:
**KERNEL Task 12 — Add tests for end-to-end behavior**

Prove the whole kernel works as one system:

- End-to-end save-path tests
- Rule suite regression tests
- Fixture-based golden tests

Today's gate:
- Passing fixtures remain passing.
- Failing fixtures block in enforce mode.
- Shadow mode does not block.
- Regression tests are deterministic across runs.

> Scope Constraints

Only work on:
- End-to-end and regression testing (Task 12 only)
- E2E tests simulating save-path evaluation, golden tests, full rule-suite regression over fixture corpus
- Test stability and determinism — minimal production code changes unless required to fix test failures

Do NOT:
- refactor unrelated systems
- introduce speculative abstractions
- modify contracts outside task scope
- add dependencies without justification

> Required Outputs

You must:
- implement the task narrowly
- write/update tests
- update documentation if architecture changes
- update internal_docs/KERNEL_DAILY_TASKS_NOTES.md
- explain architectural decisions
- explain potential failure points
- explain benchmark/performance implications if relevant

> Validation Requirements

Before finishing:
- run tests
- verify gate behavior
- ensure deterministic output
- ensure no unrelated files changed

> Reporting Format

At the end, report:
1. Files changed
2. What changed
3. Why it changed
4. Potential failure points
5. Remaining risks
6. Benchmark impact
7. Gate status

---

⇒ Day 13 — Task 13: Add performance benchmarks

⇒ Task Instructions

Today's task:
**KERNEL Task 13 — Add performance benchmarks**

Measure the kernel:

- Parse benchmark
- Rule evaluation benchmark
- End-to-end benchmark

Today's gate:
- Benchmark command runs locally.
- Benchmark output is reproducible.
- Baseline numbers are recorded in docs.

> Scope Constraints

Only work on:
- Performance benchmarks (Task 13 only)
- `benchmarks/` or equivalent, parse/rule/e2e timing harness, documented baseline results
- Measurable latency tracking — no new product features

Do NOT:
- refactor unrelated systems
- introduce speculative abstractions
- modify contracts outside task scope
- add dependencies without justification

> Required Outputs

You must:
- implement the task narrowly
- write/update tests
- update documentation if architecture changes
- update internal_docs/KERNEL_DAILY_TASKS_NOTES.md
- explain architectural decisions
- explain potential failure points
- explain benchmark/performance implications if relevant

> Validation Requirements

Before finishing:
- run tests
- verify gate behavior
- ensure deterministic output
- ensure no unrelated files changed

> Reporting Format

At the end, report:
1. Files changed
2. What changed
3. Why it changed
4. Potential failure points
5. Remaining risks
6. Benchmark impact
7. Gate status

---

⇒ Day 14 — Task 14: Add local logging and violation reporting

⇒ Task Instructions

Today's task:
**KERNEL Task 14 — Add local logging and violation reporting**

Make blocks intelligible without needing a cloud service:

- Local log format
- Human-readable violation output
- Structured machine-readable payload

Today's gate:
- A blocked file yields a clear reason.
- Logs include rule id and location.
- No required field is missing from the report.

> Scope Constraints

Only work on:
- Local logging and violation reporting (Task 14 only)
- Log format, human-readable stderr/stdout output, structured JSON payload fields (rule id, location, reason, mode)
- Reporting layer — enforcement logic must remain deterministic and unchanged in semantics

Do NOT:
- refactor unrelated systems
- introduce speculative abstractions
- modify contracts outside task scope
- add dependencies without justification

> Required Outputs

You must:
- implement the task narrowly
- write/update tests
- update documentation if architecture changes
- update internal_docs/KERNEL_DAILY_TASKS_NOTES.md
- explain architectural decisions
- explain potential failure points
- explain benchmark/performance implications if relevant

> Validation Requirements

Before finishing:
- run tests
- verify gate behavior
- ensure deterministic output
- ensure no unrelated files changed

> Reporting Format

At the end, report:
1. Files changed
2. What changed
3. Why it changed
4. Potential failure points
5. Remaining risks
6. Benchmark impact
7. Gate status

---

⇒ Day 15 — Task 15: Wrap for editor integration readiness

⇒ Task Instructions

Today's task:
**KERNEL Task 15 — Wrap for editor integration readiness**

Make the kernel ready to plug into a save hook:

- Stable command contract
- Stable output contract
- Clear integration notes

Today's gate:
- The CLI contract is stable enough for editor integration.
- The editor host can use the kernel without internal knowledge of rule mechanics.

> Scope Constraints

Only work on:
- Editor integration readiness (Task 15 only)
- CLI/output contract documentation, integration notes under `docs/`, contract stability tests
- Thin host contract only — no VS Code extension implementation in this task

Do NOT:
- refactor unrelated systems
- introduce speculative abstractions
- modify contracts outside task scope
- add dependencies without justification

> Required Outputs

You must:
- implement the task narrowly
- write/update tests
- update documentation if architecture changes
- update internal_docs/KERNEL_DAILY_TASKS_NOTES.md
- explain architectural decisions
- explain potential failure points
- explain benchmark/performance implications if relevant

> Validation Requirements

Before finishing:
- run tests
- verify gate behavior
- ensure deterministic output
- ensure no unrelated files changed

> Reporting Format

At the end, report:
1. Files changed
2. What changed
3. Why it changed
4. Potential failure points
5. Remaining risks
6. Benchmark impact
7. Gate status
