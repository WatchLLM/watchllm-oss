# Internal documentation

Agent-facing and planning context for the WatchLLM kernel repo. These files are **not** public product docs.

## Layout

| File | Purpose |
|------|---------|
| `IMPORTANT.md` | Kernel pack spec: scope, architecture rules, task gates |
| `ROADMAP.md`, `ROADMAP2.md` | Product and platform roadmaps |
| `GH_MANUAL.md` | GitHub org structure and repo operations |
| `AGENT-WORFLOW.md` | How agents should execute tasks in this repo |
| `AGENTS.md` | Agent operating rules and constraints |
| `PROMPT_TEMPLATE.md` | Copy-paste daily task prompts for agent sessions |
| `DAILY_TASKS_NOTES.md` | Org-level work log (repo setup, GitHub ops) |
| `KERNEL_DAILY_TASKS_NOTES.md` | Kernel implementation task history |
| `WatchLLM Codebase Verification.md` | Verification checklist |

## Public vs internal vs kernel specs

- **`internal_docs/`** — planning, agent workflow, org context (this directory)
- **`docs/`** — kernel implementation specs, contracts, benchmarks, codebase state
- **`../docs` repo** — ecosystem-wide architecture, RFCs, and shared specs (canonical long-term home for `docs/context/*` per `IMPORTANT.md`)
- **Repo root** — `README.md` (public), `tasks.md` (active gate tracker)
