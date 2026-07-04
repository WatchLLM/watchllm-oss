# WatchLLM Kernel Pack

## 0) Purpose

This document defines the **kernel alone** for WatchLLM: the smallest correct system that must exist before any broader platform expansion. The kernel is the deterministic local enforcement core that sits on the write path for AI-generated or human-written code and blocks structurally unsafe changes before they hit disk.

The kernel is not the cloud control plane. It is not the dashboard. It is not replay. It is not model routing. It is the local law.

The design goal is simple:

> If a file save would violate a rule, the save must be blocked deterministically, locally, and fast.

The kernel must be boring in the right way: predictable, testable, measurable, and hard to bypass.

---

## 1) Kernel scope

### In scope

* Local AST parsing for supported languages.
* Deterministic rule evaluation.
* Save-time interception in editor/CLI workflows.
* Hard block / allow decisions.
* Clear violation reporting.
* Minimal telemetry hooks for local logs.
* Repeatable test fixtures and benchmarks.
* Rule authoring and rule validation.

### Out of scope for the kernel phase

* Cloud dashboard.
* Team management.
* Org policies.
* Remote sync.
* LLM-based explanations as a dependency for enforcement.
* Replay/fork debugging.
* Agent routing.
* Semantic caching.
* Multi-user collaboration.
* Monetization features.
* General observability platform.

Those can exist later, but they are not part of the kernel.

---

## 2) Context docs

These are the canonical context documents for the kernel. They define the conceptual frame before implementation begins.

### 2.1 `docs/context/mission.md`

**Purpose:** Explain why the kernel exists.

**Contents:**

* The problem statement: autonomous agents and humans can write unsafe code at machine speed.
* The consequence: secrets, boundary violations, unsafe imports, broken auth flow, accidental destructive behavior.
* The core principle: deterministic enforcement beats heuristic post-hoc scanning.
* The product thesis: local write-path governance is the foundation.

**Acceptance criteria:**

* A new reader understands the kernel in under 2 minutes.
* The doc contains one paragraph describing the failure mode the kernel prevents.
* The doc contains one paragraph describing why AST-based enforcement is necessary.

### 2.2 `docs/context/threat-model.md`

**Purpose:** Define what the kernel must defend against.

**Contents:**

* Hardcoded secrets.
* Unsafe environment handling.
* Forbidden imports.
* Unsafe file system access.
* Service boundary violations.
* Bypass patterns from AI-generated code.
* False positive pressure from heuristic scanners.

**Acceptance criteria:**

* Threat categories are explicitly listed.
* Each threat category has an example.
* Each threat category maps to a possible deterministic rule.

### 2.3 `docs/context/glossary.md`

**Purpose:** Stabilize terms so implementation remains consistent.

**Must define:**

* Kernel
* Rule
* Violation
* Save path
* Enforce mode
* Shadow mode
* AST node
* Scope
* Safe function
* Hardcoded secret
* Boundary
* Deterministic
* Local-first

**Acceptance criteria:**

* Every term has one definition.
* No circular definitions.
* No implementation details leak into the definitions unless necessary.

### 2.4 `docs/context/language-support.md`

**Purpose:** Define supported syntax targets for the kernel MVP.

**Initial support:**

* JavaScript
* TypeScript

**Acceptance criteria:**

* The doc explicitly states that unsupported languages are out of kernel scope for now.
* The doc includes the reason for choosing these languages first.

### 2.5 `docs/context/execution-model.md`

**Purpose:** Define where and how the kernel runs.

**Contents:**

* Local execution only.
* No network dependency for enforcement.
* Save-time interception.
* CLI fallback path.
* Editor integration path.
* AST parse before decision.
* Decision before disk write.

**Acceptance criteria:**

* The enforcement path is described in exact order.
* The doc states what happens if network is unavailable.

---

## 3) Architecture rules

These are the non-negotiable rules of the kernel.

### 3.1 Determinism rule

Enforcement decisions must be deterministic for the same input source and rule set.

**Implication:**

* The same file contents must produce the same allow/block outcome.
* No LLM may be part of the enforcement decision.
* No probabilistic threshold may decide blocking.

### 3.2 Local-first rule

The kernel must not require network access to make a save decision.

**Implication:**

* The critical path must be offline-capable.
* Telemetry, if any, is secondary.
* A network failure cannot turn a block into an allow.

### 3.3 Pre-write rule

The kernel must intercept before the file is persisted to disk.

**Implication:**

* Post-commit scanning is not sufficient.
* Post-save detection is not sufficient.
* The decision must happen on the write path.

### 3.4 AST-over-text rule

The kernel must evaluate structure, not just raw strings.

**Implication:**

* Regex may be used only as a fast prefilter.
* Final judgment must inspect AST context.
* The kernel must know whether a match is in a literal, comment, argument, identifier, or safe retrieval call.

### 3.5 Explanation separation rule

Enforcement and explanation are different responsibilities.

**Implication:**

* The blocker must work without any explanation service.
* Explanations are allowed only after a deterministic violation exists.
* If explanation generation fails, enforcement must still stand.

### 3.6 Small surface rule

The kernel must stay narrow.

**Implication:**

* Do not add broad platform features into the enforcement engine.
* Do not introduce cloud-only dependencies.
* Do not turn the kernel into a product suite.

### 3.7 Rule-evidence rule

Every rule must have explicit, testable evidence.

**Implication:**

* Each rule needs sample positive and negative fixtures.
* Each rule needs a clear decision reason.
* No rule may exist without tests.

### 3.8 Failure-safe rule

When the kernel cannot parse or evaluate confidently, behavior must be explicit.

**Default policy for MVP:**

* If parsing fails, do not silently invent a decision.
* The system must surface a structured status and leave the user in control.
* The chosen fail mode must be stated in the spec and tested.

### 3.9 Performance rule

The kernel must be fast enough to disappear into the editing flow.

**Implication:**

* Save-time latency must be benchmarked.
* Hot-path operations must be minimal.
* No unnecessary process spawning on the critical path for the final kernel.

### 3.10 Portability rule

The kernel should be designed so the core logic can later move across runtimes.

**Implication:**

* Separate core logic from host integration.
* Keep the rule engine portable.
* Avoid binding the kernel architecture too tightly to one editor.

---

## 4) Specs

This is the implementable kernel specification.

## 4.1 Kernel MVP specification

### Goal

Build a local rule engine that inspects JS/TS source on save and blocks violations based on deterministic AST rules.

### Inputs

* File contents as text.
* File path.
* Language identifier.
* Rule set.
* Mode: enforce or shadow.

### Outputs

* `ALLOW` or `BLOCK` decision.
* Structured violation list if blocked.
* Rule identifiers.
* Location spans.
* Human-readable reason.
* Optional local log entry.

### Modes

#### Enforce mode

* Violations block save.
* Exit codes are non-zero in CLI flow.
* Editor integration must stop write completion.

#### Shadow mode

* Violations are recorded.
* Save is allowed.
* Output still includes the violation report.

### Rule categories in MVP

#### A. Secret literal rule

Block hardcoded credentials or secret-like literals when they appear directly in assignment contexts or dangerous call contexts.

**Examples:**

* `const key = "sk_live_..."`
* `apiToken: "..."`
* `client.secret = "..."`

**Allowed examples:**

* `process.env.STRIPE_SECRET`
* `os.getenv("STRIPE_SECRET")` if the string is a variable name, not the secret itself.

#### B. Forbidden import rule

Block dangerous imports or disallowed internal path patterns.

**Examples:**

* `child_process`
* `eval`
* `fs` if policy says so
* forbidden relative traversal beyond allowed boundaries

#### C. Boundary rule

Block module relationships that violate declared service or package boundaries.

**Examples:**

* auth module importing db internals directly
* disallowed circular dependency
* cross-boundary access to privileged internals

#### D. Auth-flow rule

For endpoint handlers, require explicit auth verification before sensitive operations.

**Examples:**

* database mutation before auth verification in the same flow
* handler execution path that reaches a protected action without required guard call

### Rule format

Each rule must define:

* `id`
* `name`
* `description`
* `scope`
* `severity`
* `match strategy`
* `decision logic`
* `allowed patterns`
* `blocked patterns`
* `test fixtures`

### Rule decision contract

Every rule must return one of:

* `PASS`
* `FAIL`
* `INCONCLUSIVE`

For MVP behavior:

* `FAIL` blocks in enforce mode.
* `PASS` allows.
* `INCONCLUSIVE` must be explicitly handled and documented.

### Logging contract

Every blocked event must log:

* timestamp
* file path
* rule id
* line/column range
* reason
* mode
* parse status

### Benchmark contract

The kernel must be benchmarked on:

* parse time
* rule evaluation time
* end-to-end save-path time
* false positive rate on curated fixtures

---

## 5) tasks.md with gates

This is the gated execution list. Do not advance a task unless its gate passes.

### Task 01 — Build the repo skeleton

**Goal:** Create the minimal repository layout for the kernel.

**Deliverables:**

* `src/`
* `tests/`
* `docs/`
* `rules/`
* `pyproject.toml` or equivalent project manifest
* `README.md`
* `tasks.md`

**Gate:**

* `python -m klyd --help` or the chosen package entrypoint runs successfully.
* Repository installs cleanly in a fresh environment.
* No placeholder imports break startup.

---

### Task 02 — Define the core data model

**Goal:** Create the internal types for files, rules, violations, and decisions.

**Deliverables:**

* Source file(s) for models/types.
* Typed decision object.
* Typed violation object.
* Typed rule interface.

**Gate:**

* Unit tests confirm the models serialize and deserialize correctly.
* A sample rule can return a structured decision object.
* No rule depends on editor-specific code.

---

### Task 03 — Implement source loading and parse entrypoint

**Goal:** Read source text and hand it to the parser pipeline.

**Deliverables:**

* File reader / stdin reader.
* Parse entrypoint.
* Language detection or explicit language parameter handling.

**Gate:**

* Test fixture source can be loaded from stdin and file path.
* Parser entrypoint returns a structured parse result.
* Invalid input is handled without crashing the process.

---

### Task 04 — Integrate AST parsing for JS/TS

**Goal:** Parse JavaScript and TypeScript into AST form.

**Deliverables:**

* JS parser integration.
* TS parser integration.
* AST normalization or wrapper.

**Gate:**

* Known JS and TS fixtures parse successfully.
* Parse tree roots are visible to tests.
* Syntax-error fixtures do not crash the parser.

---

### Task 05 — Build fixture corpus

**Goal:** Create small, explicit examples for passing and failing cases.

**Deliverables:**

* Positive and negative fixtures for secrets.
* Positive and negative fixtures for forbidden imports.
* Positive and negative fixtures for boundary violations.
* Positive and negative fixtures for auth-flow checks.

**Gate:**

* Each rule has at least one pass and one fail fixture.
* Fixtures are readable and minimal.
* Tests can load all fixtures automatically.

---

### Task 06 — Implement the secret-literal rule

**Goal:** Detect hardcoded secret patterns in structural context.

**Deliverables:**

* Rule implementation.
* AST context checks.
* Safe retrieval allowance logic.

**Gate:**

* Hardcoded secret fixtures fail.
* Env-var retrieval fixtures pass.
* Comment/string/mock false positives are not allowed to block.
* Unit tests cover at least 3 positive and 3 negative cases.

---

### Task 07 — Implement the forbidden-import rule

**Goal:** Block disallowed imports and unsafe module access paths.

**Deliverables:**

* Rule implementation.
* Allowlist/denylist structure.
* Path normalization logic.

**Gate:**

* Forbidden imports fail.
* Allowed internal imports pass.
* Relative traversal violations are detected.
* Tests prove no accidental blocking of safe imports.

---

### Task 08 — Implement the boundary rule

**Goal:** Enforce declared service/module boundaries.

**Deliverables:**

* Import graph extraction.
* Boundary map.
* Boundary enforcement logic.

**Gate:**

* Disallowed cross-boundary edges fail.
* Allowed edges pass.
* Circular dependency case is detected or explicitly excluded with a stated rule.

---

### Task 09 — Implement the auth-flow rule

**Goal:** Require auth verification before protected operations.

**Deliverables:**

* Flow-sensitive call analysis.
* Protected operation detection.
* Guard-call detection.

**Gate:**

* A handler that mutates data before auth fails.
* A handler that authenticates first passes.
* A handler with ambiguous order is either flagged or marked inconclusive by spec.

---

### Task 10 — Build the decision engine

**Goal:** Combine rules into a single deterministic evaluator.

**Deliverables:**

* Rule runner.
* Aggregator.
* Decision reduction logic.

**Gate:**

* Multiple rules can run on one source file.
* The engine returns a single coherent decision object.
* Blocking any one rule in enforce mode blocks the save.

---

### Task 11 — Build CLI interface

**Goal:** Provide a terminal entrypoint for the kernel.

**Deliverables:**

* `--stdin` support.
* File path support.
* Language flag support.
* Enforce/shadow mode switch.
* Machine-readable output.

**Gate:**

* `--help` works.
* A sample file can be evaluated from stdin.
* Exit codes are correct.
* JSON output is valid and stable.

---

### Task 12 — Add tests for end-to-end behavior

**Goal:** Prove the whole kernel works as one system.

**Deliverables:**

* End-to-end save-path tests.
* Rule suite regression tests.
* Fixture-based golden tests.

**Gate:**

* Passing fixtures remain passing.
* Failing fixtures block in enforce mode.
* Shadow mode does not block.
* Regression tests are deterministic across runs.

---

### Task 13 — Add performance benchmarks

**Goal:** Measure the kernel.

**Deliverables:**

* Parse benchmark.
* Rule evaluation benchmark.
* End-to-end benchmark.

**Gate:**

* Benchmark command runs locally.
* Benchmark output is reproducible.
* Baseline numbers are recorded in docs.

---

### Task 14 — Add local logging and violation reporting

**Goal:** Make blocks intelligible without needing a cloud service.

**Deliverables:**

* Local log format.
* Human-readable violation output.
* Structured machine-readable payload.

**Gate:**

* A blocked file yields a clear reason.
* Logs include rule id and location.
* No required field is missing from the report.

---

### Task 15 — Wrap for editor integration readiness

**Goal:** Make the kernel ready to plug into a save hook.

**Deliverables:**

* Stable command contract.
* Stable output contract.
* Clear integration notes.

**Gate:**

* The CLI contract is stable enough for editor integration.
* The editor host can use the kernel without internal knowledge of rule mechanics.

---

## 6) Kernel implementation order

This is the order I would follow.

1. Repo skeleton.
2. Core data model.
3. Source loading.
4. AST parsing.
5. Fixture corpus.
6. Secret-literal rule.
7. Forbidden-import rule.
8. Boundary rule.
9. Auth-flow rule.
10. Decision engine.
11. CLI.
12. End-to-end tests.
13. Benchmarks.
14. Logging/reporting.
15. Editor readiness.

This order is intentional: structure first, rules second, runtime third, integration last.

---

## 7) Post-kernel expansion plan

Once the kernel is stable and the gates are passing, expansion should happen in layers, not in a blob.

### Expansion A — Runtime packaging

Turn the kernel into a robust embedded runtime.

Add:

* Wasm portability path.
* Rust core if needed.
* better host integration.
* editor-native embedding.

This happens only after the Python/CLI kernel is correct.

### Expansion B — Replay and debugging

Add execution history and graph replay.

Add:

* node-by-node trace views.
* fork-from-any-node debugging.
* diff-of-decision replays.
* failure lineage.

This should use the kernel’s existing decision outputs.

### Expansion C — Architectural memory layer

This is where klyd becomes first-class.

Add:

* decision memory.
* architectural reinforcement.
* contradiction detection.
* retrieval of prior decisions at write time.

This expands the system from enforcement only into memory-assisted governance.

### Expansion D — Agent reliability suite

Add higher-order agent testing features.

Add:

* prompt injection tests.
* tool abuse detection.
* hallucination catching.
* adversarial workflow testing.

This turns WatchLLM into a broader agent reliability platform.

### Expansion E — Team/enterprise control plane

Only after local correctness and adoption exist.

Add:

* policy sync.
* org dashboards.
* audit trails.
* team configs.
* cloud explanations.
* access control.

This is the monetization and fleet-management layer.

---

## 8) Non-goals that must remain non-goals until the kernel is finished

* General AI agent platform.
* Broad observability suite.
* Enterprise dashboard.
* Cloud-first architecture.
* Multiple language support.
* Multi-product branching.
* Fancy UX that does not improve the enforcement kernel.

If a feature does not make the kernel more deterministic, faster, safer, or easier to trust, defer it.

---

## 9) Definition of done for the kernel phase

The kernel phase is done when all of the following are true:

* JS and TS parsing work.
* Core rules are implemented and tested.
* CLI works.
* Save-path enforcement works.
* Shadow/enforce modes work.
* Benchmarks exist.
* Logging exists.
* The system is stable enough to integrate into an editor hook.
* The kernel can be demonstrated on a small curated corpus without hand-waving.

---

## 10) Operating principle

Do not expand sideways before the kernel is trustworthy.

The kernel must become the thing other layers depend on.

That is the base model.
