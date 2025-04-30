# webapp/main.py

import os
from pathlib import Path

from fastapi import (
    FastAPI, Request, Depends, Form, Query, HTTPException
)
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from services.db import (
    init_db,
    register_user,               # ← импорт реального register_user
    get_workouts, add_workout,
    get_weights, add_weight,
    get_custom_programs, add_custom_program, delete_custom_program
)
from services.profile import get_user_profile, update_user_profile
from services.programs import list_goals, list_types, get_program

# === приложение и статика ===

app = FastAPI()
BASE_DIR      = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR/"static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR/"templates"))

# === стартап ===

@app.on_event("startup")
async def on_startup():
    await init_db()

# === зависимость для user_id из query ===

def require_user(user_id: str = Query(None, description="Telegram user_id")) -> int:
    if not user_id:
        raise HTTPException(400, "User_id не задан — откройте WebApp из Telegram")
    try:
        return int(user_id)
    except ValueError:
        raise HTTPException(400, f"Неверный user_id: {user_id}")

# === Home ===

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user_id: int = Depends(require_user)):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "user_id": user_id
    })

# === Profile ===

@app.get("/register")
async def register(request: Request, user_id: int = Depends(require_user)):
    # вместо выдуманного register_user_profile используем register_user
    await register_user({"id": user_id})
    return RedirectResponse(f"/profile?user_id={user_id}", status_code=302)

@app.get("/profile", response_class=HTMLResponse)
async def profile_view(request: Request, user_id: int = Depends(require_user)):
    prof = await get_user_profile(user_id)
    if not prof:
        # редиректим сразу на регистрацию, если профиля нет
        return RedirectResponse(f"/register?user_id={user_id}", status_code=302)
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "profile": prof,
        "user_id": user_id
    })

@app.post("/profile/update")
async def profile_update(
    user_id: int    = Form(...),
    first_name: str = Form(...),
    last_name: str  = Form(""),
    username: str   = Form("")
):
    await update_user_profile(user_id, first_name, last_name, username)
    return RedirectResponse(f"/profile?user_id={user_id}", status_code=302)

# === Workouts ===

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
    user_id: int        = Form(...),
    workout_type: str   = Form(...),
    duration: int       = Form(...),
    details: str        = Form("")
):
    await add_workout(user_id, workout_type, duration, details)
    return RedirectResponse(f"/workouts?user_id={user_id}", status_code=302)

# === Weight ===

@app.get("/weight", response_class=HTMLResponse)
async def weight_list(request: Request, user_id: int = Depends(require_user)):
    rows = await get_weights(user_id)
    return templates.TemplateResponse("weight.html", {
        "request": request,
        "weights": rows,
        "user_id": user_id
    })

@app.post("/weight/add")
async def weight_add(
    user_id: int   = Form(...),
    weight: float  = Form(...)
):
    await add_weight(user_id, weight)
    return RedirectResponse(f"/weight?user_id={user_id}", status_code=302)

# === Programs ===

@app.get("/programs", response_class=HTMLResponse)
async def programs_home(request: Request, user_id: int = Depends(require_user)):
    return templates.TemplateResponse("programs.html", {
        "request": request,
        "goals": list_goals(),
        "user_id": user_id
    })

@app.post("/programs/generate", response_class=HTMLResponse)
async def programs_generate(
    request: Request,
    user_id: int   = Form(...),
    goal: str      = Form(...),
    p_type: str    = Form(...)
):
    program = get_program(goal, p_type) or {}
    return templates.TemplateResponse("programs_result.html", {
        "request": request,
        "program": program,
        "user_id": user_id
    })

# === Custom Programs ===

@app.get("/programs/custom", response_class=HTMLResponse)
async def custom_list(request: Request, user_id: int = Depends(require_user)):
    progs = await get_custom_programs(user_id)
    return templates.TemplateResponse("custom_programs.html", {
        "request": request,
        "programs": progs,
        "user_id": user_id
    })

@app.post("/programs/custom/add")
async def custom_add(
    user_id: int   = Form(...),
    prog: str      = Form(...)
):
    await add_custom_program(user_id, prog)
    return RedirectResponse(f"/programs/custom?user_id={user_id}", status_code=302)

@app.post("/programs/custom/delete")
async def custom_delete(
    user_id: int   = Form(...),
    prog_id: int   = Form(...)
):
    await delete_custom_program(user_id, prog_id)
    return RedirectResponse(f"/programs/custom?user_id={user_id}", status_code=302)
