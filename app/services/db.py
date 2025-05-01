# services/db.py
import aiosqlite

DB_PATH = "app.db"  # или ваш путь к файлу БД

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # если ещё нет таблицы users
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )""")
        await db.commit()

async def register_user(data: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        # data должен содержать "username" и "password"
        await db.execute(
            "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
            (data["username"], data["password"])
        )
        await db.commit()

async def get_user(username: str, password: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, username FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        row = await cursor.fetchone()
        return row  # None, если не найден; иначе кортеж (id, username)
