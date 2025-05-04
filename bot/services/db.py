# bot/services/db.py

from pathlib import Path
import aiosqlite

# —— Настраиваем путь к базе —— 
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = str(DATA_DIR / "bot.sqlite")


async def init_db():
    """
    Создаёт три таблицы, если их ещё нет:
    - users: для регистрации telegram_id
    - workouts: для хранения тренировок
    - custom_programs: для пользовательских программ
    """
    print(f">>> Connecting to SQLite at {DB_PATH}")
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица пользователей
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id   INTEGER UNIQUE NOT NULL,
                username      TEXT
            );
        """)
        # Таблица тренировок
        await db.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER NOT NULL,
                workout_type  TEXT NOT NULL,
                duration      INTEGER,
                details       TEXT,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(telegram_id)
            );
        """)
        # Таблица кастомных программ
        await db.execute("""
            CREATE TABLE IF NOT EXISTS custom_programs (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER NOT NULL,
                program       TEXT NOT NULL,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(telegram_id)
            );
        """)
        await db.commit()


async def register_user(user):
    """
    Регистрирует пользователя Telegram в таблице users,
    если такого telegram_id ещё нет.
    """
    telegram_id = user.id
    username    = user.username or ""

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO users (telegram_id, username)
            VALUES (?, ?);
            """,
            (telegram_id, username)
        )
        await db.commit()


async def add_workout(user_id: int, workout_type: str, duration: int = None, details: str = None):
    """
    Сохраняет тренировку для пользователя.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO workouts (user_id, workout_type, duration, details)
            VALUES (?, ?, ?, ?);
            """,
            (user_id, workout_type, duration, details)
        )
        await db.commit()


async def get_workouts(user_id: int, limit: int = 10):
    """
    Возвращает список последних тренировок пользователя.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT id, workout_type, duration, details, created_at
              FROM workouts
             WHERE user_id = ?
             ORDER BY created_at DESC
             LIMIT ?;
            """,
            (user_id, limit)
        )
        rows = await cursor.fetchall()
        return rows


async def add_custom_program(user_id: int, program: str):
    """
    Добавляет новую кастомную программу для пользователя.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO custom_programs (user_id, program)
            VALUES (?, ?);
            """,
            (user_id, program)
        )
        await db.commit()


async def get_custom_programs(user_id: int):
    """
    Возвращает все кастомные программы пользователя.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT id, program, created_at
              FROM custom_programs
             WHERE user_id = ?
             ORDER BY created_at DESC;
            """,
            (user_id,)
        )
        rows = await cursor.fetchall()
        return rows


async def delete_custom_program(user_id: int, program_id: int):
    """
    Удаляет указанную программу (по id) у пользователя.
    Возвращает True, если удаление было успешным.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            DELETE FROM custom_programs
             WHERE user_id = ? AND id = ?;
            """,
            (user_id, program_id)
        )
        await db.commit()
        return cursor.rowcount > 0
