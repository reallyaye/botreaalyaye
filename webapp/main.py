from fastapi import FastAPI, Request, Depends, Form, HTTPException, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from services.db import init_db, get_workouts, add_workout
from services.profile import get_user_profile

app = FastAPI()

BASE_DIR      = Path(__file__).resolve().parent
STATIC_DIR    = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.on_event("startup")
async def startup():
    await init_db()

def require_user(user_id: str = Query(None, description="Telegram user_id")) -> int:
    if not user_id:
        # вернётся JSON { "detail": "User_id не задан — откройте из Telegram" }
        raise HTTPException(400, "User_id не задан — откройте WebApp из Telegram")
    try:
        return int(user_id)
    except ValueError:
        raise HTTPException(400, f"Неверный user_id: {user_id}")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/register")
async def register(request: Request, user_id: int = Depends(require_user)):
    from services.db import register_user
    await register_user({"id": user_id})
    # после регистрации переходим к профилю
    return RedirectResponse(f"/profile?user_id={user_id}", status_code=302)

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, user_id: int = Depends(require_user)):
    prof = await get_user_profile(user_id)
    if not prof:
        raise HTTPException(404, "Профиль не найден")
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "profile": prof
    })

@app.get("/workouts", response_class=HTMLResponse)
async def workouts_list(request: Request, user_id: int = Depends(require_user)):
    rows = await get_workouts(user_id, limit=10)
    return templates.TemplateResponse("workouts.html", {
        "request": request,
        "workouts": rows,
        "user_id": user_id
    })

@app.post("/workouts/add")
async def workouts_add(
    user_id: int = Form(...),
    workout_type: str = Form(...),
    duration: int = Form(...),
    details: str = Form(""),
):
    await add_workout(
        user_id=user_id,
        workout_type=workout_type,
        duration=duration,
        details=details
    )
    return RedirectResponse(f"/workouts?user_id={user_id}", status_code=302)
