import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, select, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from passlib.context import CryptContext
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Загружаем .env автоматически из корня проекта
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("WEBAPP_URL")
print(f"DATABASE_URL: {DATABASE_URL}")  # Отладочный вывод
print(f"TELEGRAM_TOKEN: {TELEGRAM_TOKEN}")  # Отладочный вывод
print(f"APP_URL: {APP_URL}")  # Отладочный вывод

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

class Workout(Base):
    __tablename__ = "workouts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity = Column(String, nullable=False)
    intensity = Column(String, nullable=False)
    duration = Column(Float, nullable=False)  # В минутах
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

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

async def add_workout(user_id: int, activity: str, intensity: str, duration: float, comment: str = None) -> None:
    async with AsyncSessionLocal() as session:
        workout = Workout(user_id=user_id, activity=activity, intensity=intensity, duration=duration, comment=comment)
        session.add(workout)
        await session.commit()

async def get_user_workouts(user_id: int, limit: int = 5):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Workout.activity)
            .where(Workout.user_id == user_id)
            .order_by(Workout.created_at.desc())
            .limit(limit)
        )
        return [row.activity for row in result.fetchall()]

async def get_all_user_workouts(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Workout.id, Workout.activity, Workout.intensity, Workout.duration, Workout.comment, Workout.created_at)
            .where(Workout.user_id == user_id)
            .order_by(Workout.created_at.desc())
        )
        return result.fetchall()

async def get_workout_by_id(workout_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Workout)
            .where(Workout.id == workout_id)
        )
        return result.scalars().first()

async def update_workout(workout_id: int, activity: str, intensity: str, duration: float, comment: str = None):
    async with AsyncSessionLocal() as session:
        workout = await get_workout_by_id(workout_id)
        if workout:
            workout.activity = activity
            workout.intensity = intensity
            workout.duration = duration
            workout.comment = comment
            session.add(workout)
            await session.commit()

async def delete_workout(workout_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Workout).where(Workout.id == workout_id))
        workout = result.scalars().first()
        if workout:
            await session.delete(workout)
            await session.commit()

async def get_user_stats(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(
                func.count().label("total_workouts"),
                func.sum(Workout.duration).label("total_minutes")
            )
            .where(Workout.user_id == user_id)
        )
        stats = result.first()
        return {
            "total_workouts": stats.total_workouts or 0,
            "total_minutes": stats.total_minutes or 0
        }

async def get_weekly_stats(user_id: int):
    async with AsyncSessionLocal() as session:
        # Получаем дату начала недели (7 дней назад от текущей даты)
        start_date = datetime.utcnow() - timedelta(days=7)
        
        # Общая статистика за последние 7 дней
        result = await session.execute(
            select(
                func.count().label("total_workouts"),
                func.sum(Workout.duration).label("total_minutes")
            )
            .where(Workout.user_id == user_id)
            .where(Workout.created_at >= start_date)
        )
        stats = result.first()

        # Самые частые активности за последние 7 дней
        activities_result = await session.execute(
            select(Workout.activity, func.count().label("activity_count"))
            .where(Workout.user_id == user_id)
            .where(Workout.created_at >= start_date)
            .group_by(Workout.activity)
            .order_by(func.count().desc())
            .limit(3)
        )
        top_activities = [{"activity": row.activity, "count": row.activity_count} for row in activities_result.fetchall()]

        return {
            "total_workouts": stats.total_workouts or 0,
            "total_minutes": stats.total_minutes or 0,
            "top_activities": top_activities
        }

async def get_monthly_stats(user_id: int):
    async with AsyncSessionLocal() as session:
        # Получаем дату начала месяца (30 дней назад от текущей даты)
        start_date = datetime.utcnow() - timedelta(days=30)
        
        # Общая статистика за последние 30 дней
        result = await session.execute(
            select(
                func.count().label("total_workouts"),
                func.sum(Workout.duration).label("total_minutes")
            )
            .where(Workout.user_id == user_id)
            .where(Workout.created_at >= start_date)
        )
        stats = result.first()

        # Разбивка по активностям за последние 30 дней
        activities_result = await session.execute(
            select(Workout.activity, func.sum(Workout.duration).label("total_duration"))
            .where(Workout.user_id == user_id)
            .where(Workout.created_at >= start_date)
            .group_by(Workout.activity)
        )
        activity_breakdown = [{"activity": row.activity, "duration": row.total_duration or 0} for row in activities_result.fetchall()]

        return {
            "total_workouts": stats.total_workouts or 0,
            "total_minutes": stats.total_minutes or 0,
            "activity_breakdown": activity_breakdown
        }

async def get_monthly_activity_trend(user_id: int):
    async with AsyncSessionLocal() as session:
        # Получаем данные за последние 30 дней
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        # Получаем данные о тренировках
        result = await session.execute(
            select(
                func.strftime('%Y-%m-%d', Workout.created_at).label('date'),
                func.count().label("workout_count")
            )
            .where(Workout.user_id == user_id)
            .where(Workout.created_at >= start_date)
            .group_by(func.strftime('%Y-%m-%d', Workout.created_at))
            .order_by(func.strftime('%Y-%m-%d', Workout.created_at))
        )
        trend_data = {row.date: row.workout_count for row in result.fetchall()}

        # Создаём список всех дней за последние 30 дней
        trend = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            trend.append({"date": date_str, "count": trend_data.get(date_str, 0)})
            current_date += timedelta(days=1)

        return trend