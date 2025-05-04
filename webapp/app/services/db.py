# webapp/app/services/db.py
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, select, Float, DateTime
from sqlalchemy.sql import func
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("WEBAPP_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL не задана в .env")
if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN не задан в .env")
if not APP_URL:
    raise RuntimeError("WEBAPP_URL не задан в .env")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    goal = Column(String, nullable=True)
    activity_level = Column(String, nullable=True)
    workout_types = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    telegram_id = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def register_user(username: str, password: str) -> None:
    if not password:
        raise ValueError("Пароль обязателен")
    hashed_pw = hash_password(password)
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == username))
        if result.scalars().first():
            raise ValueError("Пользователь с таким именем уже существует")
        user = User(username=username, password=hashed_pw)
        session.add(user)
        await session.commit()

async def authenticate_user(username: str, password: str) -> User | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        if user and verify_password(password, user.password):
            return user
        return None

async def get_user_by_id(user_id: int) -> User | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

async def update_user_profile(user_id: int, name: str, age: int, height: float, weight: float, goal: str,
                             activity_level: str, workout_types: str, avatar_url: str = None, telegram_id: str = None) -> None:
    async with AsyncSessionLocal() as session:
        user = await get_user_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        user.name = name
        user.age = age
        user.height = height
        user.weight = weight
        user.goal = goal
        user.activity_level = activity_level
        user.workout_types = workout_types
        user.avatar_url = avatar_url
        user.telegram_id = telegram_id
        session.add(user)
        await session.commit()

async def get_profile_history(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User.updated_at, User.name, User.age, User.height, User.weight, User.goal)
            .where(User.id == user_id)
            .order_by(User.updated_at.desc())
        )
        return result.fetchall()