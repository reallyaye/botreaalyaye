import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.db import init_db
from app.routers import auth, dashboard  
BASE_DIR = Path(__file__).parent.parent

app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "changeme!"),
    session_cookie="session"
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "app" / "templates")


@app.on_event("startup")
async def on_startup():
    # создаём таблицы, если их нет
    await init_db()


# Первый маршрут — попадаем сюда и видим форму логина/регистрации
Jinja2TemplatesResponse = None

@app.get("/", response_class=Jinja2TemplatesResponse)
async def root(request: Request):
    user_id = request.session.get("user_id")
    if user_id:
        return RedirectResponse("/dashboard")
    return templates.TemplateResponse("login.html", {"request": request})


# подключаем роутер аутентификации
app.include_router(auth.router, prefix="", tags=["auth"])
# подключите дальше свои роутеры, например:
# app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
