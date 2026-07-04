# Agent Workflow — WatchLLM Infrastructure Development

# 0) Purpose

This document defines the operational workflow between:
- human architect,
- coding agents,
- repositories,
- gates,
- RFCs,
- and infrastructure constraints.

This workflow exists to prevent:
- architectural entropy,
- uncontrolled abstraction,
- infrastructure drift,
- and agent-induced system incoherence.

The workflow itself is part of the architecture.

---

# 1) Core Principle

Agents generate implementation.

Humans preserve architecture.

The human defines:
- direction,
- boundaries,
- constraints,
- contracts,
- and invariants.

The agent executes narrowly within those constraints.

Agents are NOT autonomous architects.

---

# 2) Development Philosophy

The system must evolve through:
- irreversible primitives,
- stable contracts,
- measurable correctness,
- and sequential hardening.

NOT through:
- uncontrolled feature velocity,
- speculative abstractions,
- or demo-driven engineering.

Infrastructure quality compounds slowly.

Entropy compounds quickly.

The workflow exists to keep quality compounding faster than entropy.

---

# 3) Operational Loop

The canonical loop:

```text
1. Human defines task
2. Human defines gate
3. Human defines scope
4. Agent implements narrowly
5. Agent writes tests
6. Agent updates notes/docs
7. Human reviews architecture
8. Gates validated
9. Merge
10. Next task unlocked
````

No task skips gates.

No architectural mutation without review.

---

# 4) Task Structure

Every task MUST contain:

* objective
* explicit scope
* explicit non-goals
* gate
* validation requirements
* reporting requirements

Example:

```text
TASK-003
Objective:
Implement AST traversal abstraction.

Scope:
- traversal interface
- DFS traversal utility
- parser integration

Do NOT:
- redesign parser architecture
- add plugin systems
- modify rule engine

Gate:
- traversal tests pass
- benchmark regression < 5%
- fixtures pass
```

---

# 5) Gate Philosophy

Gates are mandatory.

A task is NOT complete because:

* code exists,
* tests compile,
* or implementation looks correct.

A task is complete ONLY when:

* gates pass deterministically.

---

# 6) Gate Types

## Functional Gates

Examples:

* parser works
* traversal works
* enforcement blocks correctly

---

## Regression Gates

Examples:

* previous fixtures still pass
* known bypasses remain blocked

---

## Performance Gates

Examples:

* latency budget maintained
* memory allocation ceiling respected

---

## Structural Gates

Examples:

* architecture boundaries preserved
* contracts unchanged
* no unrelated files modified

---

## Documentation Gates

Examples:

* specs updated
* notes updated
* RFC updated if required

---

# 7) RFC Triggers

An RFC is REQUIRED for:

* parser redesign
* rule engine redesign
* schema changes
* runtime boundary changes
* replay model changes
* persistence model changes
* language abstraction changes
* enforcement semantics changes
* event contract changes

NO implementation before RFC review.

---

# 8) Scope Control

Agents MUST remain inside task scope.

Agents may NOT:

* opportunistically refactor unrelated systems
* introduce speculative abstractions
* create new architectural layers
* split repos
* introduce new dependencies casually

Out-of-scope ideas should be documented, NOT implemented.

---

# 9) Daily Notes Discipline

Every task MUST update:

```text
internal_docs/KERNEL_DAILY_TASKS_NOTES.md
```

This creates:

* operational continuity,
* architectural memory,
* debugging history,
* and future onboarding context.

The notes are infrastructure artifacts.

Not optional logs.

---

# 10) Required Reporting

At the end of every task, the agent MUST report:

1. Files changed
2. What changed
3. Why it changed
4. Potential failure points
5. Remaining risks
6. Benchmark impact
7. Gate status

Incomplete reporting = incomplete task.

---

# 11) Testing Rules

Every meaningful implementation requires tests.

Every bug:
-> regression fixture.

Every bypass:
-> adversarial fixture.

Every false positive:
-> precision fixture.

Never remove failing fixtures to force green tests.

---

# 12) Fixture Philosophy

Fixtures are sacred infrastructure.

Fixtures become:

* truth sets,
* benchmark baselines,
* regression protection,
* reliability evidence,
* and future trust assets.

Protect them aggressively.

---

# 13) Benchmark Discipline

Benchmarking starts immediately.

Track:

* parse latency
* traversal latency
* rule evaluation latency
* end-to-end latency
* memory usage where relevant

Performance drift must become visible early.

---

# 14) Determinism Requirements

Kernel enforcement MUST remain deterministic.

The same:

* input
* rules
* config
* runtime conditions

must produce:

* identical outputs.

No probabilistic enforcement.

No hidden LLM decisions.

No cloud dependency for core behavior.

---

# 15) Documentation Discipline

Docs are part of the system.

Every subsystem should eventually contain:

* architecture docs
* specs
* testing philosophy
* threat model
* trust model
* benchmarks
* examples

Undocumented architecture eventually becomes broken architecture.

---

# 16) Event Discipline

Event schemas are foundational.

Replay/debugging depends entirely on:

* stable events,
* stable payloads,
* stable semantics.

Event changes require careful review.

---

# 17) Repo Discipline

Do NOT create repos casually.

New repos require:

* stable boundaries
* mature contracts
* justified separation

Early repo sprawl destroys coherence.

---

# 18) Dependency Discipline

Prefer:

* minimal dependencies
* portable libraries
* deterministic tooling
* stable ecosystems

Avoid:

* trend-driven tooling
* massive frameworks
* unnecessary runtime layers

Infrastructure should remain explainable.

---

# 19) Human Responsibilities

The human architect is responsible for:

* architectural direction
* subsystem boundaries
* RFC approval
* roadmap sequencing
* gate definitions
* invariant preservation
* long-horizon coherence

The human is the final authority on architecture.

---

# 20) Agent Responsibilities

The agent is responsible for:

* implementation
* scoped execution
* testing
* fixtures
* benchmarks
* documentation updates
* operational reporting

The agent is NOT responsible for:

* strategic architecture
* repo topology
* system philosophy
* long-term product direction

---

# 21) Merge Requirements

A merge is allowed ONLY if:

* gates pass
* tests pass
* benchmarks acceptable
* scope respected
* docs updated
* architecture preserved

Velocity never overrides integrity.

---

# 22) Failure Handling

If a gate fails:

DO NOT:

* bypass the gate
* weaken tests
* remove fixtures
* silently ignore regressions

Instead:

* diagnose
* document
* iterate
* harden

Infrastructure trust is built during failure handling.

---

# 23) Long-Term Principle

Every task should answer:

> Does this deepen the substrate?

If yes:
continue.

If no:
defer.

The substrate is the company.

Everything else is downstream.
