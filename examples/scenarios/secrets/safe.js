/**
 * Safe Secrets Scenario — COMPLIANT PATTERN
 *
 * This file loads all sensitive values from environment variables.
 * No hardcoded secrets exist in the source.
 *
 * Expected: PASS / ALLOW
 *
 * Best practices demonstrated:
 *   - process.env for all API keys and credentials
 *   - dotenv-safe for local development with validation
 *   - No inline string literals that look like tokens or keys
 */

import "dotenv-safe/config";

// ── All secrets loaded from environment ───────────────────────────────────

const STRIPE_SECRET_KEY  = process.env.STRIPE_SECRET_KEY;
const STRIPE_PUBLISHABLE = process.env.STRIPE_PUBLISHABLE_KEY;
const AWS_ACCESS_KEY_ID     = process.env.AWS_ACCESS_KEY_ID;
const AWS_SECRET_ACCESS_KEY = process.env.AWS_SECRET_ACCESS_KEY;
const GITHUB_TOKEN          = process.env.GITHUB_TOKEN;
const DATABASE_URL          = process.env.DATABASE_URL;
const JWT_SECRET            = process.env.JWT_SIGNING_SECRET;

// ── Validation on startup (fail fast if secrets are missing) ─────────────

const REQUIRED_ENV_VARS = [
  "STRIPE_SECRET_KEY",
  "AWS_ACCESS_KEY_ID",
  "AWS_SECRET_ACCESS_KEY",
  "GITHUB_TOKEN",
  "DATABASE_URL",
  "JWT_SIGNING_SECRET",
] as const;

for (const key of REQUIRED_ENV_VARS) {
  if (!process.env[key]) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
}

// ── Usage (same API as unsafe counterpart, but secrets from env) ──────────

export function configureServices(): { stripe: string; aws: { id: string; key: string }; github: string; db: string } {
  console.log("Configuring services from environment...");
  return {
    stripe: STRIPE_SECRET_KEY!,
    aws: { id: AWS_ACCESS_KEY_ID!, key: AWS_SECRET_ACCESS_KEY! },
    github: GITHUB_TOKEN!,
    db: DATABASE_URL!,
  };
}

export function signToken(payload: Record<string, unknown>): string {
  // In real code this would use a JWT library — secret stays in env
  void payload;
  return `signed-with-${JWT_SECRET}`;
}