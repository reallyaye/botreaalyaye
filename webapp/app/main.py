import os
from pathlib import Path
from fastapi import FastAPI, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from datetime import datetime
from aiogram import Bot, Router, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, func
import aiohttp
import secrets
import asyncio
from webapp.app.services.db import init_db, User, get_user_by_id, get_user_workouts, get_user_stats, get_user_goals, check_achieved_goals, AsyncSessionLocal

# корень каталога webapp/app
BASE_DIR = Path(__file__).resolve().parent

# подгружаем .env из корня проекта
load_dotenv(BASE_DIR.parent.parent / ".env")

# инициализируем нашу БД
from webapp.app.routers import auth, dashboard, workouts, stats, profile, goals

app = FastAPI()

# сессии для логина/логаута
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "changeme!"),
    session_cookie="session",
)

# статика с явным указанием MIME-типов
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static", html=True),
    name="static"
)

# шаблоны
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Добавляем фильтр datetimeformat для форматирования даты
def datetimeformat(value, format="%d.%m.%Y %H:%M"):
    if isinstance(value, datetime):
        return value.strftime(format)
    return value

# Регистрируем фильтр и добавляем отладочный вывод
print("Регистрирую фильтр datetimeformat")  # Отладочный вывод
templates.env.filters["datetimeformat"] = datetimeformat
print("Фильтр datetimeformat зарегистрирован")  # Отладочный вывод

# Telegram Bot
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("WEBAPP_URL")
WEBHOOK_PATH = "/telegram/webhook"
WEBHOOK_URL = f"{APP_URL}{WEBHOOK_PATH}"

# Инициализация бота и диспетчера
session = AiohttpSession()
bot = Bot(token=BOT_TOKEN, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
router = Router()

# Создаём клавиатуру с кнопкой для открытия веб-приложения
webapp_button = InlineKeyboardButton(text="Открыть веб-приложение", web_app=types.WebAppInfo(url=APP_URL))
webapp_keyboard = InlineKeyboardMarkup(inline_keyboard=[[webapp_button]])

# Фоновая задача для проверки достижения целей
async def check_goals_task():
    while True:
        try:
            achieved_goals = await check_achieved_goals()
            for goal, user in achieved_goals:
                if user.telegram_id:
                    goal_description = ""
                    if goal.goal_type == "calories":
                        goal_description = f"Сжечь {goal.target_value} калорий"
                    elif goal.goal_type == "workouts":
                        goal_description = f"Провести {goal.target_value} тренировок"
                    elif goal.goal_type == "duration":
                        goal_description = f"Тренироваться {goal.target_value} минут"
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=f"🎉 Поздравляем, {user.username}!\nВы достигли цели: {goal_description}!",
                        parse_mode=ParseMode.HTML
                    )
        except Exception as e:
            print(f"Ошибка при проверке целей: {e}")
        await asyncio.sleep(300)  # Проверяем каждые 5 минут

@app.on_event("startup")
async def on_startup():
    await init_db()
    # Запускаем фоновую задачу для проверки целей
    asyncio.create_task(check_goals_task())
    # Временно отключаем установку вебхука для устранения конфликта
    # await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    # print(f"Webhook установлен: {WEBHOOK_URL}")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()

# Обработчик команды /start
@router.message(Command(commands=["start"]))
async def send_welcome(message: types.Message):
    await message.reply(
        "Привет! Это твой фитнес-бот.\nИспользуй /link <username> для связки с профилем или нажми кнопку ниже, чтобы открыть веб-приложение.",
        reply_markup=webapp_keyboard
    )

# Обработчик команды /link
@router.message(Command(commands=["link"]))
async def link_profile(message: types.Message):
    args = message.text.split()
    if len(args) == 2:
        username = args[1]
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.username == username))
            user = result.scalars().first()
            if user:
                user.telegram_id = str(message.chat.id)
                session.add(user)
                await session.commit()
                await message.reply(
                    f"Профиль {username} успешно связан с вашим Telegram!\nТеперь ты можешь открыть веб-приложение.",
                    reply_markup=webapp_keyboard
                )
            else:
                await message.reply("Пользователь не найден.")
    else:
        await message.reply("Используйте: /link <username>")

# Обработчик вебхука
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    update = types.Update(**await request.json())
    await router.process_update(update)
    return Response(status_code=200)

@app.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)

@app.get("/clear-session")
async def clear_session(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    print("Получен запрос к /")  # Отладочный вывод
    # Генерируем CSRF-токен
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_hex(16)
    is_authenticated = bool(request.session.get("user_id"))
    print(f"Пользователь авторизован: {is_authenticated}")  # Отладочный вывод
    user = None
    stats = {"total_workouts": 0, "total_calories": 0, "total_minutes": 0}
    recent_activities = []
    user_weight = None
    goals = []
    calories_result = request.session.pop("calories_result", None)
    error = request.session.pop("error", None)

    if is_authenticated:
        user_id = request.session.get("user_id")
        print(f"User ID: {user_id}")  # Отладочный вывод
        async with AsyncSessionLocal() as session:
            print("Открываю сессию с БД")  # Отладочный вывод
            # Получаем пользователя
            user = await get_user_by_id(user_id)
            print(f"Пользователь найден: {user.username if user else None}")  # Отладочный вывод
            if user:
                user_weight = user.weight
                # Получаем статистику тренировок
                stats = await get_user_stats(user_id)
                print(f"Статистика: {stats}")  # Отладочный вывод
                # Получаем последние действия
                recent_activities = await get_user_workouts(user_id, limit=5)
                print(f"Последние действия: {recent_activities}")  # Отладочный вывод
                # Получаем цели пользователя
                goals = await get_user_goals(user_id)
                print(f"Цели: {goals}")  # Отладочный вывод

    print("Рендеринг шаблона home.html")  # Отладочный вывод
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "is_authenticated": is_authenticated,
            "username": user.username if user else None,
            "recent_activities": recent_activities,
            "stats": stats if stats else {"total_workouts": 0, "total_calories": 0, "total_minutes": 0},
            "user_weight": user_weight,
            "goals": goals,
            "calories_result": calories_result,
            "error": error,
            "current_year": datetime.now().year,
            "csrf_token": request.session.get("csrf_token")
        }
    )

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
        async with session.post("https://api.telegram.org/v1/completions", headers=headers, json=payload) as response:
            if response.status != 200:
                raise Exception(f"Ошибка API Grok: {response.status} - {await response.text()}")
            data = await response.json()
            met_str = data.get("choices", [{}])[0].get("text", "3.0").strip()
            try:
                return float(met_str)
            except ValueError:
                return 3.0  # Значение по умолчанию, если ИИ вернул некорректный формат

@app.post("/calculate-calories", response_class=HTMLResponse)
async def calculate_calories(request: Request, csrf_token: str = Form(...)):
    print("Получен запрос к /calculate-calories")  # Отладочный вывод
    if csrf_token != request.session.get("csrf_token"):
        request.session["error"] = "Недействительный CSRF-токен."
        return RedirectResponse("/", status_code=302)
    is_authenticated = bool(request.session.get("user_id"))
    if not is_authenticated:
        print("Пользователь не авторизован, перенаправляю на /login")  # Отладочный вывод
        return RedirectResponse("/login", status_code=302)

    form = await request.form()
    activity = form.get("activity")
    intensity = form.get("intensity")
    print(f"Активность: {activity}, Интенсивность: {intensity}")  # Отладочный вывод
    try:
        duration = float(form.get("duration"))
        weight = float(form.get("weight", 70))  # Вес по умолчанию 70 кг
        print(f"Длительность: {duration}, Вес: {weight}")  # Отладочный вывод
    except (ValueError, TypeError):
        request.session["error"] = "Пожалуйста, введите корректные числовые значения."
        print("Ошибка: некорректные числовые значения")  # Отладочный вывод
        return RedirectResponse("/", status_code=302)

    if duration <= 0 or weight <= 0:
        request.session["error"] = "Длительность и вес должны быть больше 0."
        print("Ошибка: длительность или вес <= 0")  # Отладочный вывод
        return RedirectResponse("/", status_code=302)

    # Получаем MET от Grok
    try:
        met = await get_met_from_grok(activity, intensity)
        print(f"Полученное значение MET: {met}")  # Отладочный вывод
    except Exception as e:
        print(f"Ошибка при запросе MET от Grok: {e}")
        met = 3.0  # Значение по умолчанию в случае ошибки

    # Расчёт калорий: MET × вес (кг) × длительность (часы)
    duration_hours = duration / 60
    calories_burned = met * weight * duration_hours
    print(f"Рассчитанные калории: {calories_burned}")  # Отладочный вывод

    request.session["calories_result"] = calories_burned
    return RedirectResponse("/", status_code=302)

# подключаем роутеры
app.include_router(auth.router, prefix="", tags=["auth"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(workouts.router, prefix="/workouts", tags=["workouts"])
app.include_router(stats.router, prefix="/stats", tags=["stats"])
app.include_router(profile.router, prefix="/profile", tags=["profile"])
app.include_router(goals.router, prefix="/goals", tags=["goals"])