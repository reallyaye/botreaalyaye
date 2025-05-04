# webapp/app/routers/auth.py
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from webapp.app.services.db import authenticate_user, register_user, AsyncSessionLocal, User
from sqlalchemy import select

router = APIRouter()
templates = Jinja2Templates(directory="webapp/app/templates")

# --- показываем форму логина ---
@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "is_authenticated": False})

# --- обрабатываем логин ---
@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        user = await authenticate_user(username, password)
        if not user:
            return templates.TemplateResponse("login.html", {"request": request, "error": "Неверные данные", "is_authenticated": False})
        request.session["user_id"] = user.id
        return RedirectResponse("/dashboard", status_code=302)
    except Exception as e:
        return templates.TemplateResponse("login.html", {"request": request, "error": f"Ошибка: {str(e)}", "is_authenticated": False})

# --- показываем форму регистрации ---
@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "is_authenticated": False})

# --- обрабатываем регистрацию ---
@router.post("/register", response_class=HTMLResponse)
async def register(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.username == username))
            if result.scalars().first():
                return templates.TemplateResponse("register.html", {"request": request, "error": "Пользователь уже существует", "is_authenticated": False})
        await register_user(username, password)
        user = await authenticate_user(username, password)
        request.session["user_id"] = user.id
        return RedirectResponse("/dashboard", status_code=302)
    except Exception as e:
        return templates.TemplateResponse("register.html", {"request": request, "error": f"Ошибка: {str(e)}", "is_authenticated": False})