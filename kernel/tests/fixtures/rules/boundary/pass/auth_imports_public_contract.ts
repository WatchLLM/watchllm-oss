import { getUserById } from "../db/public";

export function loadAuthUser(id: string) {
  return getUserById(id);
}
