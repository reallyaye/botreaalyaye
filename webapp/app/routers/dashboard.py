# webapp/app/routers/dashboard.py
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import aiogram
import os
from pathlib import Path
from dotenv import load_dotenv
from webapp.app.services.db import get_user_by_id, User

load_dotenv(Path(__file__).parent.parent.parent / ".env")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = aiogram.Bot(token=TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None

router = APIRouter()
templates = Jinja2Templates(directory="webapp/app/templates")

# 1) Функция проверки сессии
async def get_current_user(request: Request):
    uid = request.session.get("user_id")
    if not uid:
        return RedirectResponse("/login", status_code=302)
    user = await get_user_by_id(uid)
    if not user:
        request.session.clear()  # Очищаем сессию, если пользователь не найден
        return RedirectResponse("/login", status_code=302)
    return user

# 2) Эндпоинт dashboard с зависимостью
@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: User = Depends(get_current_user)
):
    if isinstance(user, RedirectResponse):
        return user  # Если get_current_user вернул редирект, возвращаем его
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user_id": user.id,
            "username": user.username,
            "telegram_id": user.telegram_id,
            "is_authenticated": True,
            "success": request.session.pop("success", None),
            "error": request.session.pop("error", None)
        }
    )

# 3) Отправка сообщения в Telegram с использованием aiogram
@router.post("/send-message", response_class=HTMLResponse)
async def send_message(
    request: Request,
    message: str = Form(...),
    user: User = Depends(get_current_user)
):
    if isinstance(user, RedirectResponse):
        return user
    if not bot or not user.telegram_id:
        request.session["error"] = "Telegram не подключен или бот не настроен"
        return RedirectResponse("/dashboard", status_code=302)
    try:
        await bot.send_message(chat_id=user.telegram_id, text=message)
        request.session["success"] = "Сообщение отправлено!"
    except Exception as e:
        request.session["error"] = f"Ошибка: {str(e)}"
    return RedirectResponse("/dashboard", status_code=302)