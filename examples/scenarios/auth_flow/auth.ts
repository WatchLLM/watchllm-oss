/**
 * Simulated authentication module for the auth-flow scenario.
 *
 * This is shared by both safe and unsafe handlers — the difference is in
 * WHEN (not whether) auth verification is called.
 */

interface AuthResult {
  valid: boolean;
  userId?: string;
}

export const auth = {
  async verify(token: string): Promise<AuthResult> {
    // Simulate auth verification — in real code this would validate a JWT
    if (!token || token === "invalid") {
      return { valid: false };
    }
    return { valid: true, userId: "user-001" };
  },
};