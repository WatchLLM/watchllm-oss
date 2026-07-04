# WatchLLM Scenarios

This directory contains self-contained example codebases used as WatchLLM Kernel
validation targets.

Each scenario demonstrates either:

- A **FAIL** outcome: code intentionally violates a WatchLLM rule, or
- A **PASS** outcome: code demonstrates the safe/compliant pattern.

## Scenario Index

| Scenario | Status | Expected Outcomes | Description |
| --- | --- | --- | --- |
| `secrets/` | ✅ Complete | PASS & FAIL | Hardcoded secrets vs. environment-based config |
| `boundaries/` | ✅ Complete | FAIL | Cross-boundary imports from frontend into internal backend |
| `auth_flow/` | ✅ Complete | FAIL | Database mutations before authentication guards |

## Directory Layout

```
scenarios/
├── README.md
├── secrets/
│   ├── README.md
│   ├── unsafe.js    ← FAIL: hardcoded credentials
│   └── safe.js      ← PASS: env-based config
├── boundaries/
│   ├── README.md
│   ├── frontend/
│   │   └── handler.ts    ← FAIL: imports from backend/internal
│   └── backend/
│       ├── internal/
│       │   ├── database.ts
│       │   └── crypto.ts
│       └── services/
│           └── user.ts
└── auth_flow/
    ├── README.md
    ├── auth.ts
    ├── db.ts
    ├── unsafe.ts     ← FAIL: mutation before auth
    └── safe.ts       ← PASS: auth before mutation
```

## Running Checks

From the repository root:

```bash
watchllm-kernel check scenarios/
```

Or target a single scenario:

```bash
watchllm-kernel check scenarios/secrets/
```

## Notes

- Scenario directories are intentionally isolated from each other.
- Unsafe files are expected to trigger WatchLLM Kernel BLOCK decisions.
- Safe files are expected to pass validation with ALLOW.
- The `db.ts` and `auth.ts` utility files in `auth_flow/` are shared by both safe
  and unsafe handlers — the violation is in *when* auth is called, not *whether*.