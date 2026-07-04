⇒ WatchLLM Examples — 4-Day Prompt Pack

Copy **one full day block** below into your agent session. Each block uses the same template; only task, gate, and scope placeholders are filled from `internal_docs/IMPORTANT.md`.

**Repo:** `watchllm/examples` (local: `d:\watchllm\examples`)

---

⇒ Day 01 — Task 01: Skeleton

⇒ Task Instructions

Today's task:
**EXAMPLES Task 01 — Skeleton**
Set up the `scenarios/` directory with a basic layout and a global README.

Today's gate:
- Structure is created.

> Scope Constraints
Only work on: `scenarios/` root files (Task 01 only).

---

⇒ Day 02 — Task 02: Secrets Scenario

⇒ Task Instructions

Today's task:
**EXAMPLES Task 02 — Secrets Scenario**
Write `scenarios/secrets/unsafe.py` (with hardcoded API keys) and `scenarios/secrets/safe.py` (using os.getenv).

Today's gate:
- Both files exist with clearly documented intent.

> Scope Constraints
Only work on: `scenarios/secrets/` directory (Task 02 only).

---

⇒ Day 03 — Task 03: Boundaries Scenario

⇒ Task Instructions

Today's task:
**EXAMPLES Task 03 — Boundaries Scenario**
Write `scenarios/boundaries/` containing a `frontend` and `backend` directory, demonstrating illegal imports.

Today's gate:
- Codebase exists showing the architectural violation.

> Scope Constraints
Only work on: `scenarios/boundaries/` directory (Task 03 only).

---

⇒ Day 04 — Task 04: Auth Flow Scenario

⇒ Task Instructions

Today's task:
**EXAMPLES Task 04 — Auth Flow Scenario**
Write `scenarios/auth_flow/` demonstrating a database mutation without preceding authentication logic.

Today's gate:
- Codebase exists showing the logic flow vulnerability.

> Scope Constraints
Only work on: `scenarios/auth_flow/` directory (Task 04 only).
