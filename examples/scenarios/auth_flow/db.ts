/**
 * Simulated database module for the auth-flow scenario.
 *
 * Provides user mutation operations that the handler calls.
 * The violation is not in the DB module — it's in the handler that
 * calls mutations before authenticating.
 */

export const db = {
  user: {
    async update(userId: string, data: Record<string, unknown>): Promise<void> {
      console.log(`[db] updating user ${userId} with`, data);
    },

    async delete(userId: string): Promise<void> {
      console.log(`[db] deleting user ${userId}`);
    },
  },
};