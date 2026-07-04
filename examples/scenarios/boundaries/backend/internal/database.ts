/**
 * Backend Internal — Database Layer
 *
 * These modules live inside the restricted backend boundary and should NOT
 * be imported by frontend code.
 *
 * The frontend should only access data through a public API contract
 * (e.g., REST endpoints or a well-defined service interface), never by
 * importing internal database/crypto modules directly.
 */

// ── Internal database client ──────────────────────────────────────────────

export class InternalDbClient {
  constructor(private readonly env: string) {}

  connect(): void {
    console.log(`[db] connecting to ${this.env} database...`);
  }

  query(sql: string): unknown[] {
    console.log(`[db] executing: ${sql}`);
    return [];
  }
}

export async function queryInternalDb(sql: string): Promise<unknown[]> {
  const client = new InternalDbClient("internal");
  return client.query(sql);
}

// ── Internal crypto utilities ─────────────────────────────────────────────

export function hashPassword(password: string): string {
  // This should never be callable from frontend code
  return `hashed:${Buffer.from(password).toString("base64")}`;
}