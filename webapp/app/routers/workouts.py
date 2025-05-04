# webapp/app/routers/workouts.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from webapp.app.services.db import get_user_by_id, User

router = APIRouter()
templates = Jinja2Templates(directory="webapp/app/templates")

# Функция проверки сессии (переиспользуем из dashboard.py)
async def get_current_user(request: Request):
    uid = request.session.get("user_id")
    if not uid:
        return RedirectResponse("/login", status_code=302)
    user = await get_user_by_id(uid)
    if not user:
        request.session.clear()
        return RedirectResponse("/login", status_code=302)
    return user

# Эндпоинт для тренировок
@router.get("/", response_class=HTMLResponse)
async def workouts(
    request: Request,
    user: User = Depends(get_current_user)
):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse(
        "workouts.html",
        {
            "request": request,
            "user_id": user.id,
            "username": user.username,
            "is_authenticated": True
        }
    )