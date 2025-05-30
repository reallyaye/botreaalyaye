from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from webapp.app.services.db import authenticate_user, register_user, get_user_by_id, AsyncSessionLocal, User
from sqlalchemy import select
import secrets

router = APIRouter()
templates = Jinja2Templates(directory="webapp/app/templates")

# --- показываем форму логина ---
@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    # Генерируем CSRF-токен
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_hex(16)
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "is_authenticated": False,
            "csrf_token": request.session.get("csrf_token")
        }
    )

# --- обрабатываем логин ---
@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...), csrf_token: str = Form(...)):
    # Проверяем CSRF-токен
    if csrf_token != request.session.get("csrf_token"):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Недействительный CSRF-токен.",
                "is_authenticated": False,
                "csrf_token": request.session.get("csrf_token")
            }
        )

    # Проверяем, пришёл ли пользователь через Telegram
    telegram_id = request.session.get("telegram_id")
    if telegram_id:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.telegram_id == telegram_id))
            user = result.scalars().first()
            if user:
                request.session["user_id"] = user.id
                return RedirectResponse("/dashboard", status_code=302)

    # Обычная авторизация через логин и пароль
    try:
        user = await authenticate_user(username, password)
        if not user:
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": "Неверные данные",
                    "is_authenticated": False,
                    "csrf_token": request.session.get("csrf_token")
                }
            )
        request.session["user_id"] = user.id
        return RedirectResponse("/dashboard", status_code=302)
    except Exception as e:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": f"Ошибка: {str(e)}",
                "is_authenticated": False,
                "csrf_token": request.session.get("csrf_token")
            }
        )

# --- показываем форму регистрации ---
@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    # Генерируем CSRF-токен
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_hex(16)
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "is_authenticated": False,
            "csrf_token": request.session.get("csrf_token")
        }
    )

# --- обрабатываем регистрацию ---
@router.post("/register", response_class=HTMLResponse)
async def register(request: Request, username: str = Form(...), password: str = Form(...), csrf_token: str = Form(...)):
    # Проверяем CSRF-токен
    if csrf_token != request.session.get("csrf_token"):
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Недействительный CSRF-токен.",
                "is_authenticated": False,
                "csrf_token": request.session.get("csrf_token")
            }
        )

    # Проверяем, пришёл ли пользователь через Telegram
    telegram_id = request.session.get("telegram_id")
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.username == username))
            if result.scalars().first():
                return templates.TemplateResponse(
                    "register.html",
                    {
                        "request": request,
                        "error": "Пользователь уже существует",
                        "is_authenticated": False,
                        "csrf_token": request.session.get("csrf_token")
                    }
                )
            await register_user(username, password)
            user = await authenticate_user(username, password)
            if telegram_id:
                user.telegram_id = telegram_id
                session.add(user)
                await session.commit()
            request.session["user_id"] = user.id
            return RedirectResponse("/dashboard", status_code=302)
    except Exception as e:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": f"Ошибка: {str(e)}",
                "is_authenticated": False,
                "csrf_token": request.session.get("csrf_token")
            }
        )

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