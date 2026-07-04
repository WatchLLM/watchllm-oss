# Secrets Scenario

This scenario demonstrates detection of hardcoded secrets and the preferred safe
alternative of loading sensitive values from the environment.

## Intent

Hardcoded credentials, API keys, tokens, and passwords should fail validation
because they expose sensitive data directly in source code.

Environment-based configuration should pass validation because secrets are
supplied outside the repository.

## Files

| File | Expected Outcome | Description |
| --- | --- | --- |
| `unsafe.js` | FAIL / BLOCK | Contains 6 types of hardcoded secrets: Stripe keys, AWS credentials, GitHub PAT, DB connection string with password, and a JWT signing secret. |
| `safe.js` | PASS / ALLOW | Identical API surface, but all secrets loaded from `process.env` with startup validation. Uses `dotenv-safe`. |

## Violations in unsafe.js

1. **Stripe API keys**: `sk_live_*` and `pk_test_*` patterns embedded as string literals
2. **AWS credentials**: Access key ID + secret access key pair in plaintext
3. **GitHub PAT**: `github_pat_*` token pattern
4. **Database URL**: Connection string with embedded `admin:SuperSecret123!` credentials
5. **JWT Secret**: Hardcoded signing key used in token generation

## Run the Check

From the repository root:

```bash
watchllm-kernel check scenarios/secrets/
```

### Expected Result

- **unsafe.js**: BLOCK — multiple hardcoded credential literals detected
- **safe.js**: ALLOW — no string literal matches any credential pattern; all values loaded from environment