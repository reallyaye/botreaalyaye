# webapp/app/services/db.py
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, select, func
from passlib.context import CryptContext
from dotenv import load_dotenv

# Подгружаем переменные окружения из корня проекта
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Читаем URL базы данных (например: "sqlite+aiosqlite:///./db.sqlite3")
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL не задана в .env")

# Настройка SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=True)  # echo=True для отладки, отключить в продакшене
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
Base = declarative_base()

# Модель пользователя
class User(Base):
    __tablename__ = "users"
    id          = Column(Integer, primary_key=True, index=True)
    username    = Column(String, unique=True, index=True, nullable=False)
    password    = Column(String, nullable=True)  # Может быть None для Telegram
    telegram_id = Column(String, unique=True, nullable=True)  # Telegram ID

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# Создание таблиц при старте приложения
async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Регистрация нового пользователя (хешируем пароль)
async def register_user(username: str, password: str = None, telegram_id: str = None) -> None:
    hashed_pw = hash_password(password) if password else None
    async with AsyncSessionLocal() as session:
        # Проверяем, есть ли пользователь с таким именем
        result = await session.execute(select(User).where(User.username == username))
        if result.scalars().first():
            raise ValueError("Пользователь с таким именем уже существует")
        user = User(username=username, password=hashed_pw, telegram_id=telegram_id)
        session.add(user)
        await session.commit()

# Аутентификация: ищем пользователя и проверяем пароль
async def authenticate_user(username: str, password: str) -> User | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        if user and user.password and verify_password(password, user.password):
            return user
        return None

# Поиск пользователя по ID
async def get_user_by_id(user_id: int) -> User | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

# Поиск пользователя по Telegram ID
async def get_user_by_telegram_id(telegram_id: str) -> User | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalars().first()