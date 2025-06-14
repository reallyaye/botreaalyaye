from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import secrets
from datetime import datetime
from typing import Optional
import bcrypt
import os

from ..database import AsyncSessionLocal, get_db
from ..models import User
from ..templates_config import templates
from webapp.app.services.db import authenticate_user, register_user, get_user_by_id

router = APIRouter(prefix="/auth", tags=["auth"])

# Создаём класс для current_user
class CurrentUser:
    def __init__(self, user=None, is_authenticated=False):
        self.is_authenticated = is_authenticated
        self.username = user.username if user else None
        self.weight = getattr(user, 'weight', None)

# --- показываем форму логина ---
@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    current_user = CurrentUser()
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "current_user": current_user,
            "csrf_token": request.session.get("csrf_token")
        }
    )

# --- обрабатываем логин ---
@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    if csrf_token != request.session.get("csrf_token"):
        raise HTTPException(status_code=400, detail="Invalid CSRF token")

    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalars().first()

    if not user or user.password != password:  # В реальном приложении проверять хэш пароля
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "current_user": CurrentUser(),
                "error": "Неверное имя пользователя или пароль",
                "csrf_token": request.session.get("csrf_token")
            }
        )

    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=302)

# --- показываем форму регистрации ---
@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    # Создаём current_user для шаблона
    current_user = CurrentUser()

    # Генерируем CSRF-токен
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_hex(16)

    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "current_user": current_user,
            "csrf_token": request.session.get("csrf_token")
        }
    )

# --- обрабатываем регистрацию ---
@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    name: str = Form(...),
    last_name: str = Form(...),
    age: int = Form(...),
    height: float = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    activity_level: str = Form(...),
    workout_types: str = Form(...),
    csrf_token: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    if csrf_token != request.session.get("csrf_token"):
        raise HTTPException(status_code=400, detail="Invalid CSRF token")

    # Проверяем, существует ли пользователь
    result = await db.execute(select(User).where(User.username == username))
    if result.scalars().first():
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "current_user": CurrentUser(),
                "error": "Пользователь с таким именем уже существует",
                "csrf_token": request.session.get("csrf_token")
            }
        )

    # Создаём нового пользователя
    user = User(
        username=username,
        password=password,  # В реальном приложении пароль должен быть хэширован
        email=email,
        name=name,
        last_name=last_name,
        age=age,
        height=height,
        weight=weight,
        goal=goal,
        activity_level=activity_level,
        workout_types=workout_types,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(user)
    await db.commit()

    # Автоматически логиним пользователя
    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=302)

# --- Роут для получения Telegram ID (будет вызываться из Telegram Web App) ---
@router.get("/telegram-auth", response_class=RedirectResponse)
async def telegram_auth(request: Request):
    telegram_id = request.query_params.get("id")
    if telegram_id:
        request.session["telegram_id"] = telegram_id
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.telegram_id == telegram_id))
            user = result.scalars().first()
            if user:
                request.session["user_id"] = user.id
                return RedirectResponse("/dashboard", status_code=302)
    return RedirectResponse("/login", status_code=302)