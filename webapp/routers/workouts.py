from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from services.db import add_workout, get_workouts

router = APIRouter()
templates = Jinja2Templates(directory="webapp/templates")

@router.get("/")
async def list_workouts(request: Request):
    user_id = request.query_params.get("user_id")
    if not user_id:
        return templates.TemplateResponse("error.html", {"request": request, "msg": "user_id не задан"})
    uid = int(user_id)
    workouts = await get_workouts(uid, limit=50)
    return templates.TemplateResponse("workouts.html", {"request": request, "workouts": workouts, "user_id": uid})

@router.post("/add")
async def add_workout_web(request: Request,
                          user_id: int = Form(...),
                          workout_type: str = Form(...),
                          duration: int = Form(...),
                          details: str | None = Form(None)):
    await add_workout(user_id, workout_type, duration, details)
    return RedirectResponse(f"/workouts/?user_id={user_id}", status_code=303)
