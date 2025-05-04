# webapp/app/routers/profile.py
from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from webapp.app.services.db import get_user_by_id, update_user_profile, get_profile_history, User, AsyncSessionLocal
from starlette.responses import RedirectResponse as StarletteRedirectResponse
import os
from pathlib import Path
import uuid
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties  # Новый импорт

router = APIRouter()
templates = Jinja2Templates(directory="webapp/app/templates")
session = AiohttpSession()
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"), session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# Функция проверки сессии
async def get_current_user(request: Request):
    uid = request.session.get("user_id")
    if not uid:
        return StarletteRedirectResponse("/login", status_code=302)
    user = await get_user_by_id(uid)
    if not user:
        request.session.clear()
        return StarletteRedirectResponse("/login", status_code=302)
    return user

# Эндпоинт для профиля
@router.get("/", response_class=HTMLResponse)
async def profile(
    request: Request,
    user: User = Depends(get_current_user)
):
    if isinstance(user, StarletteRedirectResponse):
        return user
    history = await get_profile_history(user.id)
    progress = calculate_progress(user.weight, user.goal, user.height, user.age) if user.weight and user.height and user.age else 0
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user_id": user.id,
            "username": user.username,
            "name": user.name or "",
            "age": user.age or "",
            "height": user.height or "",
            "weight": user.weight or "",
            "goal": user.goal or "maintain",
            "activity_level": user.activity_level or "sedentary",
            "workout_types": user.workout_types or "",
            "avatar_url": user.avatar_url or "",
            "is_authenticated": True,
            "success": request.session.pop("success", None),
            "error": request.session.pop("error", None),
            "history": history,
            "progress": progress
        }
    )

# Эндпоинт для обновления профиля
@router.post("/update", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    user: User = Depends(get_current_user),
    name: str = Form(...),
    age: int = Form(...),
    height: float = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    activity_level: str = Form(...),
    workout_types: str = Form(...),
    avatar: UploadFile = File(None)
):
    if isinstance(user, StarletteRedirectResponse):
        return user
    if not (0 < age <= 120) or height <= 0 or weight <= 0:
        request.session["error"] = "Некорректные данные (возраст: 1-120, рост и вес > 0)"
        return RedirectResponse("/profile", status_code=302)
    
    avatar_url = user.avatar_url
    if avatar:
        try:
            file_ext = os.path.splitext(avatar.filename)[1]
            new_filename = f"{uuid.uuid4()}{file_ext}"
            static_dir = Path("webapp/app/static/avatars")
            static_dir.mkdir(exist_ok=True)
            file_path = static_dir / new_filename
            with open(file_path, "wb") as buffer:
                buffer.write(await avatar.read())
            avatar_url = new_filename
        except Exception as e:
            request.session["error"] = f"Ошибка загрузки аватара: {str(e)}"
            return RedirectResponse("/profile", status_code=302)

    try:
        await update_user_profile(user.id, name, age, height, weight, goal, activity_level, workout_types, avatar_url)
        request.session["success"] = "Профиль успешно обновлен!"
        # Отправка уведомления в Telegram
        if user.telegram_id:
            await bot.send_message(chat_id=user.telegram_id, text=f"Профиль {user.username} обновлен!\nИмя: {name}\nВес: {weight} кг\nЦель: {goal}")
    except Exception as e:
        request.session["error"] = f"Ошибка: {str(e)}"
    return RedirectResponse("/profile", status_code=302)

# Функция расчета прогресса
def calculate_progress(weight: float, goal: str, height: float, age: int) -> float:
    if not all([weight, height, age]):
        return 0
    bmi = weight / ((height / 100) ** 2)
    target_bmi = 22.5 if goal == "maintain" else (20 if goal == "lose" else 25)
    target_weight = target_bmi * ((height / 100) ** 2)
    progress = min(100, max(0, ((weight - target_weight) / (weight - target_weight if goal == "lose" else target_weight - weight)) * 100)) if weight != target_weight else 100
    return progress