import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, select, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from passlib.context import CryptContext
from dotenv import load_dotenv
from datetime import datetime, timedelta
import aiohttp

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
    calories_burned = Column(Float, nullable=True)  # Сожжённые калории
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity = Column(String, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    reminder_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_type = Column(String, nullable=False)  # Например, "calories", "workouts", "duration"
    target_value = Column(Float, nullable=False)  # Целевое значение (например, 5000 калорий)
    deadline = Column(DateTime, nullable=False)  # Дедлайн для достижения цели
    achieved = Column(Boolean, default=False)  # Флаг достижения цели
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
        print(f"DEBUG: Найден пользователь: {user}")
        if user:
            print(f"DEBUG: Введённый пароль: {password}")
            print(f"DEBUG: Хеш из БД: {user.password}")
            try:
                check = verify_password(password, user.password)
            except Exception as e:
                print(f"DEBUG: Ошибка при проверке пароля: {e}")
                check = False
            print(f"DEBUG: Проверка пароля: {check}")
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

async def get_met_from_grok(activity: str, intensity: str) -> float:
    # Формируем запрос к API Grok
    prompt = (
        f"Estimate the MET (Metabolic Equivalent of Task) value for the activity '{activity}' "
        f"with {intensity} intensity. Provide only the numerical MET value (e.g., 7.0) without any additional text."
    )
    
    # Используем API xAI (предполагаем, что у вас есть API-ключ в .env)
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise ValueError("XAI_API_KEY не задан в .env")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "max_tokens": 10,
        "temperature": 0.7
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.x.ai/v1/completions", headers=headers, json=payload) as response:
            if response.status != 200:
                raise Exception(f"Ошибка API Grok: {response.status} - {await response.text()}")
            data = await response.json()
            met_str = data.get("choices", [{}])[0].get("text", "3.0").strip()
            try:
                return float(met_str)
            except ValueError:
                return 3.0  # Значение по умолчанию, если ИИ вернул некорректный формат

async def add_workout(user_id: int, activity: str, intensity: str, duration: float, comment: str = None) -> None:
    async with AsyncSessionLocal() as session:
        # Получаем пользователя для получения его веса
        user = await get_user_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        # Используем вес пользователя или 70 кг по умолчанию
        weight = user.weight if user and user.weight else 70

        # Получаем MET от Grok
        try:
            met = await get_met_from_grok(activity, intensity)
        except Exception as e:
            print(f"Ошибка при запросе MET от Grok: {e}")
            met = 3.0  # Значение по умолчанию

        # Расчёт калорий: MET × вес (кг) × длительность (часы)
        duration_hours = duration / 60
        calories_burned = met * weight * duration_hours

        # Сохраняем тренировку с калориями
        workout = Workout(
            user_id=user_id,
            activity=activity,
            intensity=intensity,
            duration=duration,
            calories_burned=calories_burned,
            comment=comment
        )
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
            select(Workout.id, Workout.activity, Workout.intensity, Workout.duration, Workout.calories_burned, Workout.comment, Workout.created_at)
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
            # Получаем пользователя для пересчёта калорий
            user = await get_user_by_id(workout.user_id)
            if not user:
                raise ValueError("Пользователь не найден")
            
            # Используем вес пользователя или 70 кг по умолчанию
            weight = user.weight if user and user.weight else 70

            # Получаем MET от Grok
            try:
                met = await get_met_from_grok(activity, intensity)
            except Exception as e:
                print(f"Ошибка при запросе MET от Grok: {e}")
                met = 3.0  # Значение по умолчанию

            # Пересчитываем калории
            duration_hours = duration / 60
            calories_burned = met * weight * duration_hours

            # Обновляем данные тренировки
            workout.activity = activity
            workout.intensity = intensity
            workout.duration = duration
            workout.calories_burned = calories_burned
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
                func.sum(Workout.duration).label("total_minutes"),
                func.sum(Workout.calories_burned).label("total_calories")
            )
            .where(Workout.user_id == user_id)
        )
        stats = result.first()
        return {
            "total_workouts": stats.total_workouts or 0,
            "total_minutes": stats.total_minutes or 0,
            "total_calories": stats.total_calories or 0
        }

async def get_weekly_stats(user_id: int):
    async with AsyncSessionLocal() as session:
        # Получаем дату начала недели (7 дней назад от текущей даты)
        start_date = datetime.utcnow() - timedelta(days=7)
        
        # Общая статистика за последние 7 дней
        result = await session.execute(
            select(
                func.count().label("total_workouts"),
                func.sum(Workout.duration).label("total_minutes"),
                func.sum(Workout.calories_burned).label("total_calories")
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
            "total_calories": stats.total_calories or 0,
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
                func.sum(Workout.duration).label("total_minutes"),
                func.sum(Workout.calories_burned).label("total_calories")
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
            "total_calories": stats.total_calories or 0,
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

async def add_schedule(user_id: int, activity: str, scheduled_time: datetime) -> None:
    async with AsyncSessionLocal() as session:
        schedule = Schedule(user_id=user_id, activity=activity, scheduled_time=scheduled_time)
        session.add(schedule)
        await session.commit()

async def get_user_schedules(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Schedule)
            .where(Schedule.user_id == user_id)
            .where(Schedule.scheduled_time >= datetime.utcnow())
            .order_by(Schedule.scheduled_time)
        )
        return result.scalars().all()

async def delete_schedule(schedule_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Schedule).where(Schedule.id == schedule_id))
        schedule = result.scalars().first()
        if schedule:
            await session.delete(schedule)
            await session.commit()

async def get_pending_reminders():
    async with AsyncSessionLocal() as session:
        now = datetime.utcnow()
        reminder_window = now + timedelta(minutes=15)  # Напоминание за 15 минут до тренировки
        result = await session.execute(
            select(Schedule)
            .where(Schedule.scheduled_time >= now)
            .where(Schedule.scheduled_time <= reminder_window)
            .where(Schedule.reminder_sent == False)
        )
        return result.scalars().all()

async def mark_reminder_sent(schedule_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Schedule).where(Schedule.id == schedule_id))
        schedule = result.scalars().first()
        if schedule:
            schedule.reminder_sent = True
            session.add(schedule)
            await session.commit()

async def add_goal(user_id: int, goal_type: str, target_value: float, deadline: datetime) -> None:
    async with AsyncSessionLocal() as session:
        goal = Goal(
            user_id=user_id,
            goal_type=goal_type,
            target_value=target_value,
            deadline=deadline
        )
        session.add(goal)
        await session.commit()

async def get_user_goals(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Goal)
            .where(Goal.user_id == user_id)
            .where(Goal.deadline >= datetime.utcnow())
            .where(Goal.achieved == False)
            .order_by(Goal.created_at)
        )
        goals = result.scalars().all()
        # Для каждой цели рассчитываем текущий прогресс
        for goal in goals:
            if goal.goal_type == "calories":
                result = await session.execute(
                    select(func.sum(Workout.calories_burned).label("current_value"))
                    .where(Workout.user_id == user_id)
                    .where(Workout.created_at >= goal.created_at)
                    .where(Workout.created_at <= goal.deadline)
                )
            elif goal.goal_type == "workouts":
                result = await session.execute(
                    select(func.count().label("current_value"))
                    .where(Workout.user_id == user_id)
                    .where(Workout.created_at >= goal.created_at)
                    .where(Workout.created_at <= goal.deadline)
                )
            elif goal.goal_type == "duration":
                result = await session.execute(
                    select(func.sum(Workout.duration).label("current_value"))
                    .where(Workout.user_id == user_id)
                    .where(Workout.created_at >= goal.created_at)
                    .where(Workout.created_at <= goal.deadline)
                )
            else:
                continue
            current_value = result.first().current_value or 0
            goal.current_value = current_value
            goal.progress = (current_value / goal.target_value * 100) if goal.target_value > 0 else 0
        return goals

async def check_achieved_goals():
    async with AsyncSessionLocal() as session:
        # Получаем все активные цели
        result = await session.execute(
            select(Goal, User)
            .join(User, User.id == Goal.user_id)
            .where(Goal.deadline >= datetime.utcnow())
            .where(Goal.achieved == False)
        )
        goals = result.fetchall()
        achieved_goals = []
        for goal, user in goals:
            if goal.goal_type == "calories":
                result = await session.execute(
                    select(func.sum(Workout.calories_burned).label("current_value"))
                    .where(Workout.user_id == user.id)
                    .where(Workout.created_at >= goal.created_at)
                    .where(Workout.created_at <= goal.deadline)
                )
            elif goal.goal_type == "workouts":
                result = await session.execute(
                    select(func.count().label("current_value"))
                    .where(Workout.user_id == user.id)
                    .where(Workout.created_at >= goal.created_at)
                    .where(Workout.created_at <= goal.deadline)
                )
            elif goal.goal_type == "duration":
                result = await session.execute(
                    select(func.sum(Workout.duration).label("current_value"))
                    .where(Workout.user_id == user.id)
                    .where(Workout.created_at >= goal.created_at)
                    .where(Workout.created_at <= goal.deadline)
                )
            else:
                continue
            current_value = result.first().current_value or 0
            if current_value >= goal.target_value:
                goal.achieved = True
                session.add(goal)
                achieved_goals.append((goal, user))
        await session.commit()
        return achieved_goals

async def delete_goal(goal_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Goal).where(Goal.id == goal_id))
        goal = result.scalars().first()
        if goal:
            await session.delete(goal)
            await session.commit()