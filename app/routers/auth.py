import os
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy import select
from passlib.context import CryptContext

from app.db import async_session
from app.models import users
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()

def get_session_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id

@router.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": ""})

@router.post("/register")
async def register_post(request: Request, email: str = Form(...), password: str = Form(...)):
    hashed = pwd_context.hash(password)
    async with async_session() as session:
        # проверяем, есть ли уже пользователь
        exists = await session.execute(select(users.c.id).where(users.c.email == email))
        if exists.scalar_one_or_none():
            return templates.TemplateResponse("register.html", {"request": request, "error": "Email уже зарегистрирован"})
        await session.execute(users.insert().values(email=email, hashed_password=hashed))
        await session.commit()
    # логиним сразу после регистрации
    request.session["user_id"] = email
    return RedirectResponse("/dashboard", status_code=302)

@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": ""})

@router.post("/login")
async def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    async with async_session() as session:
        row = await session.execute(select(users).where(users.c.email == email))
        user = row.scalar_one_or_none()
        if not user or not pwd_context.verify(password, user.hashed_password):
            return templates.TemplateResponse("login.html", {"request": request, "error": "Неверные учётные данные"})
    request.session["user_id"] = user.id
    return RedirectResponse("/dashboard", status_code=302)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login")
