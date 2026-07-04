/**
 * Unsafe Secrets Scenario — DELIBERATE VIOLATION
 *
 * This file contains multiple hardcoded secrets that should cause the
 * WatchLLM Kernel secrets rule to BLOCK on write.
 *
 * Expected: FAIL / BLOCK
 *
 * Violations present:
 *   - Stripe API key (test-card key with sk_live_ prefix for realism)
 *   - AWS access key
 *   - GitHub personal access token
 *   - Database connection string with embedded password
 *   - JWT signing secret
 */

// ── Hardcoded API keys ────────────────────────────────────────────────────

const STRIPE_SECRET_KEY = "sk_live_51NxmJkFhX9vQpR3tL2aB7cD4eA8wZ6yPgH1j5mK_nF9oU2sT3";
const STRIPE_PUBLISHABLE  = "pk_test_T1sR2eT3aM4eP5l6E7xA8bC9dE0fG1hI2jK3lM_n4oP5";

// ── Cloud provider credentials ────────────────────────────────────────────

const AWS_ACCESS_KEY_ID     = "AKIAIOSFODNN7EXAMPLE";
const AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY";

// ── GitHub token ──────────────────────────────────────────────────────────

const GITHUB_PAT = "github_pat_11ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890";

// ── Database credentials in connection string ─────────────────────────────

const DATABASE_URL = "postgresql://admin:SuperSecret123!@db.internal.watchllm.dev:5432/production";

// ── JWT signing secret ────────────────────────────────────────────────────

const JWT_SECRET = "s3cr3t-jwt-k3y-th4t-sh0uld-n3v3r-b3-in-c0d3-2026!";

// ── Usage ─────────────────────────────────────────────────────────────────

export function configureServices(): { stripe: string; aws: { id: string; key: string }; github: string; db: string } {
  console.log("Configuring services with hardcoded secrets...");
  return {
    stripe: STRIPE_SECRET_KEY,
    aws: { id: AWS_ACCESS_KEY_ID, key: AWS_SECRET_ACCESS_KEY },
    github: GITHUB_PAT,
    db: DATABASE_URL,
  };
}

export function signToken(payload: Record<string, unknown>): string {
  // In real code this would sign a JWT — the secret itself is the violation
  void payload;
  return `signed-with-${JWT_SECRET}`;
}