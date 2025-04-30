# webapp/main.py  — или в webapp/routers/weight.py

from fastapi import FastAPI, HTTPException, Query, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from services.db import init_db, get_weights, add_weight

app = FastAPI()

BASE_DIR      = Path(__file__).resolve().parent
STATIC_DIR    = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.on_event("startup")
async def startup():
    await init_db()

def require_user(user_id: str = Query(None)) -> int:
    if not user_id:
        raise HTTPException(400, "user_id не задан — откройте из Telegram")
    return int(user_id)

# --- существующие /, /profile, /workouts, /workouts/add ---

@app.get("/weight", response_class=HTMLResponse)
async def weight_list(request: Request, user_id: int = Depends(require_user)):
    rows = await get_weights(user_id, limit=20)
    return templates.TemplateResponse("weight.html", {
        "request": request,
        "weights": rows,
        "user_id": user_id
    })

@app.post("/weight/add")
async def weight_add(
    user_id: int = Form(...),
    weight: float = Form(...)
):
    await add_weight(user_id=user_id, weight=weight)
    return RedirectResponse(f"/weight?user_id={user_id}", status_code=302)
