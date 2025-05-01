# app/routers/auth.py
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from services.db import register_user, get_user


router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login_post(username: str = Form(...), password: str = Form(...)):
    user = await get_user(username, password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    # устанавливаем сессию и редиректим на дашборд
    return RedirectResponse("/dashboard", status_code=302)
