# WatchLLM — Org and Repository Operations Manual

# 0) Purpose

This document defines exactly how the WatchLLM organization should be structured, maintained, expanded, and operated.

This is NOT generic GitHub hygiene.

The org must behave like:

* a serious infrastructure company,
* a systems research lab,
* and a long-horizon runtime engineering organization.

The org structure itself is part of the architecture.

Everything must optimize for:

* clarity,
* low entropy,
* composability,
* deterministic structure,
* and future scaling.

The goal is:

> A future contributor or agent should immediately understand the ecosystem topology.

---

# 1) Core org philosophy

The org should remain:

* infra-first
* terminal-native
* engineering-centric
* low-noise
* architecture-driven
* documentation-heavy
* anti-chaotic

Do NOT optimize for:

* startup aesthetics,
* social hype,
* excessive branding,
* trendy repo sprawl,
* random experiments in main org.

The org is infrastructure.

Infrastructure must feel:

* stable,
* intentional,
* trustworthy,
* and technically serious.

---

# 2) The actual org structure

## Primary orgs

### `watchllm/`

The main infrastructure org.

This contains:

* kernel
* runtime
* replay
* reliability
* governance
* cloud components
* official SDKs
* official integrations

This is the canonical org.

---

### `kaadipranav/`

Personal experimental space.

Allowed here:

* prototypes
* unstable experiments
* weird ideas
* temporary tooling
* drafts
* architecture playgrounds

Do NOT prematurely move everything into watchllm.

The org must stay clean.

---

### `codify/`

Can remain as:

* legacy,
* experiments,
* utilities,
* or future independent tooling.

But avoid mixing WatchLLM architecture into unrelated repos.

---

# 3) What SHOULD exist inside watchllm/

These are the canonical repos.

---

# 4) Canonical repository map

## 4.1 `kernel`

The most important repo.

### Purpose

Deterministic local enforcement engine.

### Contains

* parser abstraction
* AST traversal
* rule engine
* enforcement runtime
* save-path contracts
* benchmarks
* fixtures
* CLI

### MUST NOT contain

* cloud dashboard
* replay UI
* marketing pages
* enterprise logic
* unrelated experiments

### Status

Permanent core repository.

---

## 4.2 `klyd`

Architectural memory system.

### Contains

* commit analysis
* decision extraction
* local memory store
* retrieval engine
* contradiction detection
* injection pipeline

### MUST NOT contain

* enforcement engine internals
* replay UI
* SaaS logic

### Relationship

Consumes architectural context.
Kernel enforces resulting constraints.

---

## 4.3 `replay`

Execution replay infrastructure.

### Contains

* event graph system
* replay engine
* execution timelines
* graph storage
* fork-from-node logic

### MUST NOT contain

* direct enforcement logic
* editor integration internals

---

## 4.4 `runtime`

Governance-aware orchestration runtime.

### Contains

* runtime policies
* execution orchestration
* identity hooks
* permission systems
* runtime SDKs

---

## 4.5 `reliability`

Stress-testing and adversarial evaluation.

### Contains

* prompt injection tests
* hallucination evaluations
* adversarial workflows
* tool abuse tests
* scoring systems

---

## 4.6 `schemas`

Central schema repository.

### Contains

* event schemas
* rule schemas
* replay schemas
* telemetry schemas
* policy schemas

### Why this matters

Schemas become shared contracts.

---

## 4.7 `docs`

Central documentation.

### Contains

* RFCs
* architecture docs
* diagrams
* specifications
* trust model
* threat model
* roadmap

### Why this matters

Infra systems need durable written architecture.

---

## 4.8 `examples`

Curated demonstrations.

### Contains

* minimal examples
* attack examples
* architectural examples
* replay examples
* memory examples

### Why this matters

Examples become:

* onboarding,
* demos,
* testing aids,
* and future docs.

---

## 4.9 `benchmarks`

Performance and regression benchmarking.

### Contains

* benchmark corpus
* benchmark tooling
* regression measurements
* parser performance tests
* runtime latency tests

---

## 4.10 `vscode`

Editor integration.

### Contains

* VSCode extension
* save interception layer
* diagnostics UI
* local runtime bridge

### MUST remain thin

The extension is NOT the kernel.

It is merely a host.

---

# 5) What should NOT become separate repos

Avoid splitting too early.

DO NOT create separate repos for:

* tiny utilities
* every parser
* every rule
* tiny integrations
* random experiments
* internal scripts

Monorepo-style thinking is better early.

Only split repos when:

* boundaries are stable,
* ownership is clear,
* contracts are mature,
* or distribution genuinely benefits.

---

# 6) Branching strategy

Simple.

Do NOT over-engineer GitFlow.

---

## Main branches

### `main`

Stable.
Always runnable.

### `dev`

Optional.
Only if velocity requires it later.

---

## Feature branches

Naming:

* `feat/parser-abstraction`
* `feat/auth-flow-rule`
* `feat/event-schema`
* `fix/secret-rule-fp`
* `perf/ast-traversal`
* `rfc/replay-graph`

---

## Rules

* Never commit broken tests to main.
* Never merge speculative architecture without docs.
* Every major subsystem change requires an RFC.
* Performance regressions require explanation.

---

# 7) Commit philosophy

Commits should read like infrastructure engineering history.

Avoid:

* messy dumps
* vague commits
* giant mixed commits

Good:

* `feat(kernel): add AST traversal abstraction`
* `fix(rules): reduce secret-literal false positives`
* `perf(parser): cache traversal context`
* `docs(rfc): define event lineage model`

---

# 8) PR philosophy

Even if solo.

Treat PRs seriously.

PRs become:

* historical architecture records,
* future debugging context,
* contributor onboarding,
* and reasoning artifacts.

Every substantial PR should explain:

* why,
* tradeoffs,
* alternatives rejected,
* and performance implications.

---

# 9) Labels

Standardize labels EARLY.

## Core labels

* `kernel`
* `memory`
* `runtime`
* `replay`
* `reliability`
* `parser`
* `rules`
* `perf`
* `security`
* `docs`
* `benchmarks`
* `infra`
* `breaking-change`
* `good-first-issue`
* `research`

---

# 10) Milestones

Milestones should map to phases.

## Example

* Kernel MVP
* Wasm Runtime
* VSCode Integration
* klyd Integration
* Replay Alpha
* Reliability Harness
* Runtime Governance
* Enterprise Control Plane

---

# 11) GH CLI operational rules

The agent operating on the org MUST use GitHub CLI (`gh`) consistently.

Do NOT rely heavily on browser workflows.

The org should be terminal-native.

---

# 12) Repo creation rules

## Create repo

```bash
gh repo create watchllm/kernel \
  --public \
  --description "Deterministic runtime governance kernel for autonomous coding agents" \
  --clone
```

---

## Standard initialization

Every repo must include:

* README.md
* LICENSE
* CONTRIBUTING.md
* SECURITY.md
* ROADMAP.md
* RFCs/
* docs/
* tests/
* benchmarks/
* .editorconfig
* .gitignore

---

## Create labels

```bash
gh label create kernel --color FF5555
gh label create replay --color 55AAFF
gh label create runtime --color A855F7
gh label create perf --color F59E0B
gh label create security --color EF4444
```

---

## Create milestones

```bash
gh api repos/watchllm/kernel/milestones \
  -f title="Kernel MVP"
```

---

## Create issues

```bash
gh issue create \
  --title "Implement AST traversal abstraction" \
  --body-file docs/issues/ast_traversal.md \
  --label kernel
```

---

## Create PRs

```bash
gh pr create \
  --title "feat(kernel): add auth-flow rule engine" \
  --body-file .github/pull_request_template.md
```

---

## View status

```bash
gh issue status
gh pr status
gh repo view --web
```

---

# 13) Repository templates

Create shared templates inside:

`.github/`

---

## Required templates

### Issue templates

* bug_report.yml
* feature_request.yml
* RFC.yml
* performance_regression.yml
* security_issue.yml

---

### PR template

Must require:

* architectural reasoning
* benchmark impact
* test impact
* breaking changes
* alternatives considered

---

# 14) RFC workflow

Every major architecture change:

1. Create RFC.
2. Discuss tradeoffs.
3. Document alternatives.
4. Merge RFC.
5. Implement.

NOT:

1. Random implementation.
2. Retroactive documentation.

---

# 15) Security handling

Infrastructure repos need mature security posture EARLY.

---

## Rules

* Never commit secrets.
* Never disable checks casually.
* Every parser edge case gets documented.
* Security issues become tracked artifacts.
* Dangerous bypasses get regression fixtures.

---

## SECURITY.md

Must include:

* disclosure policy
* contact path
* supported versions
* response expectations

---

# 16) Benchmark discipline

Performance regressions should be treated seriously.

Every meaningful parser/rule/runtime change should answer:

* did latency change?
* did memory usage change?
* did traversal complexity change?
* did false-positive rate change?

---

# 17) Documentation discipline

Docs are NOT optional.

The org should feel:

* explainable,
* structured,
* research-grade.

Every subsystem should eventually have:

* architecture doc
* threat model
* trust model
* spec
* benchmarks
* examples
* RFC history

---

# 18) Release philosophy

Do NOT release constantly for hype.

Release when:

* contracts stabilize,
* quality improves,
* architecture matures.

Infrastructure trust compounds slowly.

---

# 19) Naming philosophy

Names should feel:

* terminal-native
* infra-native
* minimal
* precise
* memorable

Avoid:

* AI buzzwords
* excessive branding fluff
* long names
* gimmicks

Current naming direction is good.

---

# 20) What the org eventually becomes

The final org becomes:

* runtime infrastructure
* governance infrastructure
* replay infrastructure
* reliability infrastructure
* memory infrastructure

for autonomous software systems.

Not just:

* “AI tooling.”

The org structure should reflect that from the beginning.

---

# 21) The single most important operational rule

Do not allow entropy to scale faster than architecture.

That kills infrastructure companies.

Every repo,
Every PR,
Every RFC,
Every feature,
Every benchmark,
Every subsystem

must deepen the substrate.

That is the operating model.
