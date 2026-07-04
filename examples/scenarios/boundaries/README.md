# Boundaries Scenario

This scenario demonstrates an architectural boundary violation through forbidden
cross-domain imports.

## Intent

Application layers or domains should not directly reach into restricted internal
modules owned by another boundary.

This scenario is intended to show code that violates that rule by performing
forbidden cross-boundary access.

## Files

| File | Expected Outcome | Description |
| --- | --- | --- |
| `frontend/handler.ts` | FAIL / BLOCK | Imports from `backend/internal/database` and `backend/internal/crypto` — forbidden cross-boundary access. |
| `backend/internal/database.ts` | INTERNAL | Internal DB client and crypto utilities — should never be imported by frontend. |
| `backend/services/user.ts` | ALLOWED | Public service layer — safe entry point for frontend code. |

## Run the Check

From the repository root:

```bash
watchllm-kernel check scenarios/boundaries/
```

### Expected Result

The import from `frontend` into `backend` should be blocked by the boundaries
rule, producing a FAIL outcome.