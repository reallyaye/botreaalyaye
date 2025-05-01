# app/main.py
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.services.db import init_db
from app.routers import auth  # пока только auth
# later: from app.routers import dashboard

BASE_DIR = Path(__file__).parent.parent

app = FastAPI()

# Сессии для хранения user_id после логина
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "changeme!"),
    session_cookie="session"
)

# Статика и шаблоны
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "app" / "templates")


@app.on_event("startup")
async def on_startup():
    # создаём таблицы, если их ещё нет
    await init_db()


@app.get("/")
async def root(request: Request):
    # если в сессии есть user_id — редиректим на дашборд
    if request.session.get("user_id"):
        return RedirectResponse("/dashboard")
    # иначе показываем страницу логина/регистрации
    return templates.TemplateResponse("login.html", {"request": request})


# роуты для аутентификации
app.include_router(auth.router, prefix="", tags=["auth"])

# потом, когда напишете:
# from app.routers import dashboard
# app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
