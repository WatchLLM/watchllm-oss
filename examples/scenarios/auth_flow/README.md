# Auth Flow Scenario

This scenario demonstrates a logic-flow vulnerability where a sensitive database
mutation occurs without a preceding authentication or authorization check.

## Intent

Handlers that mutate protected data should verify the caller before performing
the mutation.

The unsafe handler performs the mutation first, then checks auth — making the
auth check useless. The safe handler checks auth first, gates the mutation, and
also verifies authorization (user can only modify their own data).

## Files

| File | Expected Outcome | Description |
| --- | --- | --- |
| `unsafe.ts` | FAIL / BLOCK | Two handlers (`updateUserHandler`, `deleteUserHandler`) that run database mutations BEFORE calling `auth.verify()`. Auth check happens after the damage is done. |
| `safe.ts` | PASS / ALLOW | Same handlers with auth verification FIRST — mutations are gated behind both authentication AND authorization checks. |
| `auth.ts` | Shared module | Simulated auth verification utility. |
| `db.ts` | Shared module | Simulated database with `user.update()` and `user.delete()` operations. |

## Violations in unsafe.ts

1. **Mutation-before-auth**: `db.user.update()` called before `auth.verify()`
2. **Destructive mutation unguarded**: `db.user.delete()` with no prior auth
3. **No authorization check**: Even if auth passes, any user can modify any other user's data

## Run the Check

From the repository root:

```bash
watchllm-kernel check scenarios/auth_flow/
```

### Expected Result

- **unsafe.ts**: BLOCK — mutations found before authentication guards
- **safe.ts**: ALLOW — all mutations occur after successful auth + authorization checks
- **auth.ts**, **db.ts**: ALLOW — utility modules, no violations