# WatchLLM Agent Operating Rules

You are operating inside a long-horizon infrastructure codebase.

This is NOT a generic AI app.
This is deterministic runtime governance infrastructure for autonomous systems.

You are NOT allowed to invent architecture casually.

You MAY:

- implement scoped tasks
- scaffold code
- write tests
- improve readability
- improve ergonomics
- improve performance if measurable
- generate fixtures
- generate benchmarks
- improve documentation
- refactor locally when explicitly justified

You MAY NOT:

- redefine subsystem boundaries
- introduce speculative abstractions
- create unnecessary repos/packages
- introduce frameworks without justification
- change contracts silently
- invent cloud dependencies
- add hidden magic
- add probabilistic enforcement behavior
- bypass deterministic guarantees
- weaken local-first architecture
- merge unrelated concerns into one subsystem

## Core Philosophy

WatchLLM is:

- deterministic
- local-first
- infrastructure-grade
- AST-aware
- runtime-oriented
- reliability-focused

The system must remain:

- explainable
- measurable
- benchmarked
- composable
- testable

Correctness > velocity.
Trust > feature count.
Determinism > intelligence.

---

# Enforcement Principles

- Enforcement decisions must be deterministic.
- The same input + same rules = same output.
- No LLM may participate in enforcement decisions.
- Enforcement must work offline.
- Save-time interception is the core path.
- AST-based analysis is preferred over regex.
- Explanations are separate from enforcement.

---

# Architectural Constraints

Do NOT:
- over-abstract early
- introduce plugin systems prematurely
- create unnecessary config layers
- create giant inheritance trees
- split repos prematurely
- build dashboards during kernel phase
- add enterprise/cloud logic to the kernel

Prefer:
- explicit code
- small interfaces
- stable contracts
- measurable performance
- low dependency count
- portable architecture

---

# RFC Rules

Major architectural changes REQUIRE RFCs before implementation.

Examples:
- parser abstraction changes
- event schema changes
- replay model changes
- runtime contract changes
- rule engine redesigns
- storage changes
- boundary model changes

Implementation without architectural reasoning is forbidden.

---

# Testing Rules

Every rule MUST have:
- positive fixtures
- negative fixtures
- regression fixtures if applicable

Every bug:
-> add regression fixture.

Every bypass:
-> add adversarial fixture.

Never remove failing fixtures to make tests pass.

---

# Benchmark Rules

Performance regressions must be visible.

Track:
- parse latency
- traversal latency
- rule evaluation latency
- end-to-end latency
- memory usage where relevant

Do not introduce complexity without measurable benefit.

---

# Documentation Rules

Every subsystem should eventually contain:
- architecture docs
- specs
- testing philosophy
- trust model
- threat model
- benchmarks
- examples

Docs are part of the infrastructure.

---

# Event Discipline

Event schemas are foundational infrastructure.

Do NOT:
- change event meaning casually
- rename events arbitrarily
- emit inconsistent payloads

Replay/debugging depends on stable events.

---

# Repo Discipline

Do NOT create new repos unless:
- boundaries are stable
- contracts are mature
- separation is justified

Avoid repo sprawl.

---

# Commit Discipline

Commits should be:
- small
- scoped
- intentional
- explainable

Good examples:
- feat(kernel): add AST traversal abstraction
- fix(rules): reduce secret literal false positives
- perf(parser): cache traversal context

Bad examples:
- misc fixes
- updates
- working version

---

# PR Discipline

Every substantial PR should explain:
- what changed
- why
- tradeoffs
- alternatives rejected
- performance implications
- testing impact

---

# Operational Rule

Do not optimize for demos.

Optimize for:
- reliability
- determinism
- composability
- future infrastructure viability

Every subsystem must deepen the substrate.