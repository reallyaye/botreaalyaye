import aiosqlite
from .db import DB_PATH

async def get_user_profile(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT user_id,username,first_name,last_name FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()
        return dict(row) if row else None

async def update_user_profile(user_id, username=None, first_name=None, last_name=None):
    fields, params = [], []
    if username is not None:
        fields.append("username=?"); params.append(username)
    if first_name is not None:
        fields.append("first_name=?"); params.append(first_name)
    if last_name is not None:
        fields.append("last_name=?"); params.append(last_name)
    if not fields:
        return
    params.append(user_id)
    query = f"UPDATE users SET {', '.join(fields)} WHERE user_id=?"
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(query, params)
        await db.commit()
