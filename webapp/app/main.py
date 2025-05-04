#webapp/app/main.py
import os
from pathlib import Path
from fastapi import FastAPI, Request, Response
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
from sqlalchemy import select

# корень каталога webapp/app
BASE_DIR = Path(__file__).resolve().parent

# подгружаем .env из корня проекта
load_dotenv(BASE_DIR.parent.parent / ".env")

# инициализируем нашу БД
from webapp.app.services.db import init_db, User, get_user_by_id, update_user_profile, AsyncSessionLocal

# роутеры
from webapp.app.routers import auth, dashboard, workouts, stats, profile

app = FastAPI()

# сессии для логина/логаута
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "changeme!"),
    session_cookie="session",
)

# статика
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

# шаблоны
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

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

@app.on_event("startup")
async def on_startup():
    await init_db()
    # Установка вебхука
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    print(f"Webhook установлен: {WEBHOOK_URL}")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()

# Обработчик команды /start
@router.message(Command(commands=["start"]))
async def send_welcome(message: types.Message):
    await message.reply("Привет! Используй /link <username> для связки с профилем.")

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
                await message.reply(f"Профиль {username} успешно связан с вашим Telegram!")
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
    is_authenticated = bool(request.session.get("user_id"))
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "is_authenticated": is_authenticated,
            "tips": [
                "Пейте больше воды — минимум 2 литра в день!",
                "Делайте разминку перед каждой тренировкой.",
                "Ставьте реалистичные цели и отслеживайте прогресс."
            ]
        }
    )

# подключаем роутеры
app.include_router(auth.router, prefix="", tags=["auth"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(workouts.router, prefix="/workouts", tags=["workouts"])
app.include_router(stats.router, prefix="/stats", tags=["stats"])
app.include_router(profile.router, prefix="/profile", tags=["profile"])