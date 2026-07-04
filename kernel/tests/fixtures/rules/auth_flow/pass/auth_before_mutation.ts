export async function handler(req, db, auth) {
  await auth.verify(req);
  await db.user.update({ id: req.userId });
}
