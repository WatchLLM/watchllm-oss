# Daily Task Notes

## Current Active Task
- Task ID: ORG-004
- Title: Fix org/profile READMEs — public-safe, no private repo index
- Gate: .github public with profile README; docs public-standard; private repos scoped
- Status: COMPLETE

---

# Work Log

## Date
2026-05-21

### Task
ORG-001 — WatchLLM GitHub org setup and repo visibility

### Objective
Align github.com/WatchLLM with GH_MANUAL: infra-first org, low entropy, canonical repo map.

### Changes Made
- Updated org description to runtime governance positioning (removed old Cloudflare-edge marketing copy).
- Disabled member repository creation (`members_can_create_repositories: false`).
- Made non-canonical public repos private: `.github`, `WATCHLLM-SDK-NODE`, `WATCHLLM-SDK-PYTHON`, `WATCHLLM`.
- Left `WATCHLLM-DOCS` public (maps to canonical `docs`).

### Gate Result
PASS

### Notes For Next Task
- Create/rename canonical repos per GH_MANUAL (`kernel`, `klyd`, `replay`, etc.) when boundaries are ready.
- Rename `WATCHLLM-CORE` → `kernel` when migration is planned.
- Update stale repo descriptions (still reference old agent-reliability/Cloudflare copy).

---

## Date
2026-05-21

### Task
ORG-002 — Canonical repo scaffolding

### Objective
Create GH_MANUAL canonical repos (kernel not built yet); clear outdated docs; archive failed WATCHLLM-CORE.

### Changes Made
- Created private repos: `kernel`, `klyd`, `replay`, `runtime`, `reliability`, `schemas`, `examples`, `benchmarks`, `vscode` with minimal README scaffolds.
- Renamed `WATCHLLM-DOCS` → `docs`; removed 9 outdated markdown files; left ecosystem table scaffold README.
- Archived `WATCHLLM-CORE` (deprecated experiment, not the kernel).

### Gate Result
PASS

### Notes For Next Task
- Enhance READMEs across canonical repos.
- Repopulate `watchllm/docs` from `watchllm-expanded/internal_docs`.
- Build kernel in `watchllm/kernel` from scratch (do not use WATCHLLM-CORE).

---

## Date
2026-05-21

### Task
ORG-003 — Archive legacy; consistent READMEs

### Changes Made
- Archived: `WATCHLLM-APP`, `.github`, `WATCHLLM-SDK-NODE`, `WATCHLLM-SDK-PYTHON`, `watchllm-cloud`, `WATCHLLM`, `WATCHLLM-INTERNAL` (plus `WATCHLLM-CORE` already archived).
- Pushed consistent README template to all 10 canonical repos via `scripts/generate-org-readmes.ps1`.
- Aligned repo descriptions on canonical repos.
- Updated legacy repo descriptions to `ARCHIVED: ...` (README file edits blocked on archived repos by GitHub).
- Added org profile README at `watchllm/.github/profile/README.md` (repo archived but profile may still display).

### Gate Result
PASS

### Notes For Next Task
- Repopulate `watchllm/docs` from internal_docs.
- Unarchive briefly only if legacy README files must be edited in-repo.

---

## Date
YYYY-MM-DD

### Task
<task name>

### Objective
<what this task was meant to achieve>

### Files Touched
- path/to/file
- path/to/file

### Changes Made
- change
- change
- change

### Architectural Reasoning
<why this implementation was chosen>

### Alternatives Considered
- option
- why rejected

### Potential Failure Points
- edge case
- parser issue
- performance concern
- false positive risk
- traversal ambiguity
- runtime concern

### Tests Added
- test name
- fixture added
- regression added

### Benchmarks
- parse latency
- traversal latency
- end-to-end latency

### Gate Result
PASS / FAIL

### Remaining Risks
- unresolved issue
- future concern
- technical debt

### Notes For Next Task
- next dependency
- blocker
- future cleanup
- required RFCs

---

# Regression Log

## Regression ID
- Cause:
- Fix:
- Fixture Added:
- Prevented Future Failure:

---

# Performance Notes

## Current Known Bottlenecks
- issue
- issue

## Future Optimization Targets
- target
- target

---

# Architectural Decisions Snapshot

## Important Decisions
- decision
- rationale
- tradeoff

---

# Open Questions

- unresolved question
- unresolved question