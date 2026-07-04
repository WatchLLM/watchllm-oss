/**
 * Unsafe Boundaries Scenario — DELIBERATE VIOLATION
 *
 * The frontend handler directly imports from a restricted backend/internal
 * module, violating architectural boundaries.
 *
 * Expected: FAIL / BLOCK
 *
 * Violations present:
 *   - Import from backend/internal/database (should be blocked by boundary rule)
 *   - Direct query execution from frontend code
 *   - Access to backend utility functions from the wrong layer
 */

import { queryInternalDb, InternalDbClient } from "../backend/internal/database";
import { hashPassword } from "../backend/internal/crypto";
import { getUserById } from "../backend/services/user";

// Direct database access from frontend — architectural violation
const db: InternalDbClient = new InternalDbClient("production");

export async function handleUserRequest(userId: string): Promise<unknown> {
  // Frontend code directly queries the database — no API layer
  const rawData = await queryInternalDb(`SELECT * FROM users WHERE id = '${userId}'`);

  // Frontend code calls backend-internal crypto
  const hashed = hashPassword("user-provided-password");

  return { user: rawData, passwordHash: hashed };
}