/**
 * Backend Services — Public API Layer
 *
 * These are the safe, allowed entry points for frontend code.
 * They live in `backend/services/` and form the public contract.
 */

import { InternalDbClient } from "../internal/database";

export async function getUserById(userId: string): Promise<unknown> {
  // This is the proper pattern: service layer owns the DB interaction
  const db = new InternalDbClient("production");
  return db.query(`SELECT * FROM users WHERE id = ?`);
}