/**
 * Unsafe Auth-Flow Scenario — DELIBERATE VIOLATION
 *
 * The request handler performs a database mutation BEFORE verifying the user's
 * authentication. This is a logic-flow vulnerability where sensitive operations
 * are reachable without prior auth checks.
 *
 * Expected: FAIL / BLOCK
 *
 * Violations present:
 *   - Mutation (db.user.update) executed before auth.verify()
 *   - No authorization check on user-scoped mutation
 *   - Auth token extracted but not validated before mutation
 */

import { db } from "./db";
import { auth } from "./auth";

interface Request {
  userId: string;
  token: string;
  body: Record<string, unknown>;
}

interface Response {
  status: number;
  data?: unknown;
  error?: string;
}

export const updateUserHandler = async (req: Request): Promise<Response> => {
  // ❌ VIOLATION: Database mutation executed BEFORE auth guard verification!
  // The status update runs regardless of whether the token is valid.
  await db.user.update(req.userId, { status: "active", updatedAt: new Date().toISOString() });

  // Auth check happens AFTER the mutation — too late.
  const authResult = await auth.verify(req.token);
  if (!authResult.valid) {
    return { status: 401, error: "Unauthorized" };
  }

  return { status: 200, data: { updated: true } };
};

export const deleteUserHandler = async (req: Request): Promise<Response> => {
  // ❌ Same violation pattern: destructive mutation before auth check
  await db.user.delete(req.userId);

  const authResult = await auth.verify(req.token);
  if (!authResult.valid) {
    // Already deleted the user — irreversible damage!
    return { status: 401, error: "Unauthorized — but user was already deleted" };
  }

  return { status: 200, data: { deleted: true } };
};