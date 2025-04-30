from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from services.db import get_workouts, add_workout

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def require_user_id(user_id: int = None):
    if not user_id:
        raise HTTPException(400, "user_id is required")
    return user_id

@router.get("/workouts", response_class=HTMLResponse)
async def list_workouts(request: Request, user_id: int = Depends(require_user_id)):
    rows = await get_workouts(user_id, limit=10)
    return templates.TemplateResponse("workouts.html", {
        "request": request,
        "workouts": rows,
        "user_id": user_id
    })

@router.post("/workouts/add")
async def add_new_workout(
    user_id: int    = Form(...),
    workout_type: str = Form(...),
    duration: int   = Form(...),
    details: str    = Form("")
):
    await add_workout(user_id, workout_type, duration, details)
    return RedirectResponse(f"/workouts?user_id={user_id}", status_code=302)
