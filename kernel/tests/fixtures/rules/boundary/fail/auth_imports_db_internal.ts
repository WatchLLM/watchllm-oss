import { rawQuery } from "../db/internal/query";

export function loadAuthUser(id: string) {
  return rawQuery("select * from users where id = ?", [id]);
}
