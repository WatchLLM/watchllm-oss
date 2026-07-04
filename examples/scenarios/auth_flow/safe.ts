/**
 * Safe Auth-Flow Scenario — COMPLIANT PATTERN
 *
 * The request handler verifies authentication FIRST, then performs the
 * database mutation. The auth guard gates all sensitive operations.
 *
 * Expected: PASS / ALLOW
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
  // ✅ Auth check BEFORE any mutation
  const authResult = await auth.verify(req.token);
  if (!authResult.valid) {
    return { status: 401, error: "Unauthorized" };
  }

  // ✅ Only the authenticated user can update their own data
  if (authResult.userId !== req.userId) {
    return { status: 403, error: "Forbidden" };
  }

  // ✅ Mutation only runs after passing all auth/authorization gates
  await db.user.update(req.userId, { status: "active", updatedAt: new Date().toISOString() });

  return { status: 200, data: { updated: true } };
};

export const deleteUserHandler = async (req: Request): Promise<Response> => {
  // ✅ Auth check first — no mutation occurs for unauthenticated requests
  const authResult = await auth.verify(req.token);
  if (!authResult.valid) {
    return { status: 401, error: "Unauthorized" };
  }

  if (authResult.userId !== req.userId) {
    return { status: 403, error: "Forbidden" };
  }

  await db.user.delete(req.userId);

  return { status: 200, data: { deleted: true } };
};