import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

# корень каталога webapp/app
BASE_DIR = Path(__file__).resolve().parent

# подгружаем .env из корня проекта
load_dotenv(BASE_DIR.parent.parent / ".env")

# инициализируем нашу БД
from webapp.app.services.db import init_db

# роутеры
from webapp.app.routers import auth, dashboard

app = FastAPI()

# сессии для логина/логаута
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "changeme!"),
    session_cookie="session",
)

# статика
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

# шаблоны из webapp/app/templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)

@app.get("/clear-session")
async def clear_session(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    is_authenticated = bool(request.session.get("user_id"))
    if is_authenticated:
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "is_authenticated": is_authenticated})

# подключаем роутеры
app.include_router(auth.router, prefix="", tags=["auth"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])