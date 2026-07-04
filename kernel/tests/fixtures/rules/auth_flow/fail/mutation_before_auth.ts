export async function handler(req, db, auth) {
  await db.user.update({ id: req.userId });
  await auth.verify(req);
}
