import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from aiogram import Bot, Dispatcher
from aiogram.types import Update

from services.db import init_db
from webapp.routers.home import router as home_router
from webapp.routers.profile import router as profile_router
from webapp.routers.workouts import router as workouts_router
from webapp.routers.dashboard import router as dashboard_router
# 1) Загрузка .env из корня
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN не задан в .env")

# 2) Создаём экземпляры Bot и Dispatcher (Dispatcher без аргументов)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 3) Настраиваем FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="webapp/static"), name="static")
templates = Jinja2Templates(directory="webapp/templates")

app.include_router(home_router, tags=["home"])
app.include_router(profile_router, prefix="/profile", tags=["profile"])
app.include_router(workouts_router, prefix="/workouts", tags=["workouts"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
@app.post("/webhook/{token}")
async def telegram_webhook(request: Request, token: str):
    if token != BOT_TOKEN:
        return {"ok": False}
    data = await request.json()
    update = Update(**data)
    await dp.process_update(update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    # Инициализация БД
    await init_db()
    # Устанавливаем webhook, если есть публичный URL
    web_url = os.getenv("WEBAPP_URL")
    if web_url:
        await bot.set_webhook(f"{web_url}/webhook/{BOT_TOKEN}", drop_pending_updates=True)
    print("✅ WebApp & DB initialized")

@app.on_event("shutdown")
async def on_shutdown():
    # Опционально удаляем webhook на остановке
    await bot.delete_webhook()
    await bot.session.close()
    print("🛑 WebApp shutdown")
