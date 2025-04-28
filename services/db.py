# services/db.py

import os
import aiosqlite

DB_PATH = os.getenv("DATABASE_URL", "./db.sqlite3")

async def init_db():
    """Инициализация базы данных: создание всех таблиц, если их не существует."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            workout_type TEXT NOT NULL,
            duration INTEGER,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        );
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            metric TEXT,
            value REAL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        );
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS custom_programs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            program TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        );
        """)
        await db.commit()

# Работа с пользователями
async def register_user(user):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users(user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
            (user.id, user.username, user.first_name, user.last_name)
        )
        await db.commit()

# Работа с тренировками
async def add_workout(user_id, workout_type, duration=None, details=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO workouts(user_id, workout_type, duration, details) VALUES (?, ?, ?, ?)",
            (user_id, workout_type, duration, details)
        )
        await db.commit()

async def get_workouts(user_id, limit=20):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id, workout_type, duration, details, created_at FROM workouts WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )
        return await cur.fetchall()

# Работа с прогрессом
async def add_progress(user_id, metric, value):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO progress(user_id, metric, value) VALUES (?, ?, ?)",
            (user_id, metric, value)
        )
        await db.commit()

async def get_progress(user_id, metric=None, limit=20):
    async with aiosqlite.connect(DB_PATH) as db:
        if metric:
            cur = await db.execute(
                "SELECT id, metric, value, recorded_at FROM progress WHERE user_id = ? AND metric = ? ORDER BY recorded_at DESC LIMIT ?",
                (user_id, metric, limit)
            )
        else:
            cur = await db.execute(
                "SELECT id, metric, value, recorded_at FROM progress WHERE user_id = ? ORDER BY recorded_at DESC LIMIT ?",
                (user_id, limit)
            )
        return await cur.fetchall()

# Работа с кастомными программами
async def add_custom_program(user_id: int, program_text: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO custom_programs(user_id, program) VALUES (?, ?)",
            (user_id, program_text)
        )
        await db.commit()

async def get_custom_programs(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id, program, created_at FROM custom_programs WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        return await cur.fetchall()

async def delete_custom_program(user_id: int, program_id: int) -> bool:
    """
    Удаляет программу по её id и user_id.
    Возвращает True, если запись была удалена, иначе False.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "DELETE FROM custom_programs WHERE id = ? AND user_id = ?",
            (program_id, user_id)
        )
        await db.commit()
        return cur.rowcount > 0
