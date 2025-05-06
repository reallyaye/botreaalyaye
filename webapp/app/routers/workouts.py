from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse as StarletteRedirectResponse
from webapp.app.services.db import get_user_by_id, add_workout, delete_workout, get_all_user_workouts, get_workout_by_id, update_workout, User

router = APIRouter()
templates = Jinja2Templates(directory="webapp/app/templates")

# Функция проверки сессии
async def get_current_user(request: Request):
    uid = request.session.get("user_id")
    if not uid:
        return StarletteRedirectResponse("/login", status_code=302)
    user = await get_user_by_id(uid)
    if not user:
        request.session.clear()
        return StarletteRedirectResponse("/login", status_code=302)
    return user

@router.get("/", response_class=HTMLResponse)
async def workouts(request: Request, user: User = Depends(get_current_user)):
    if isinstance(user, StarletteRedirectResponse):
        return user
    # Получаем все тренировки пользователя
    workouts = await get_all_user_workouts(user.id)
    return templates.TemplateResponse(
        "workouts.html",
        {
            "request": request,
            "user_id": user.id,
            "username": user.username,
            "is_authenticated": True,
            "success": request.session.pop("success", None),
            "error": request.session.pop("error", None),
            "workouts": workouts
        }
    )

@router.post("/add", response_class=HTMLResponse)
async def add_workout_route(
    request: Request,
    user: User = Depends(get_current_user),
    activity: str = Form(...),
    intensity: str = Form(...),
    duration: float = Form(...),
    comment: str = Form(None)
):
    if isinstance(user, StarletteRedirectResponse):
        return user
    try:
        await add_workout(user.id, activity, intensity, duration, comment)
        request.session["success"] = "Тренировка успешно добавлена!"
    except Exception as e:
        request.session["error"] = f"Ошибка: {str(e)}"
    return RedirectResponse("/workouts", status_code=302)

@router.get("/edit/{workout_id}", response_class=HTMLResponse)
async def edit_workout_page(request: Request, workout_id: int, user: User = Depends(get_current_user)):
    if isinstance(user, StarletteRedirectResponse):
        return user
    workout = await get_workout_by_id(workout_id)
    if not workout or workout.user_id != user.id:
        request.session["error"] = "Тренировка не найдена или доступ запрещён."
        return RedirectResponse("/workouts", status_code=302)
    return templates.TemplateResponse(
        "workouts.html",
        {
            "request": request,
            "user_id": user.id,
            "username": user.username,
            "is_authenticated": True,
            "success": request.session.pop("success", None),
            "error": request.session.pop("error", None),
            "workouts": await get_all_user_workouts(user.id),
            "edit_workout": workout
        }
    )

@router.post("/update/{workout_id}", response_class=HTMLResponse)
async def update_workout_route(
    request: Request,
    workout_id: int,
    user: User = Depends(get_current_user),
    activity: str = Form(...),
    intensity: str = Form(...),
    duration: float = Form(...),
    comment: str = Form(None)
):
    if isinstance(user, StarletteRedirectResponse):
        return user
    workout = await get_workout_by_id(workout_id)
    if not workout or workout.user_id != user.id:
        request.session["error"] = "Тренировка не найдена или доступ запрещён."
        return RedirectResponse("/workouts", status_code=302)
    try:
        await update_workout(workout_id, activity, intensity, duration, comment)
        request.session["success"] = "Тренировка успешно обновлена!"
    except Exception as e:
        request.session["error"] = f"Ошибка: {str(e)}"
    return RedirectResponse("/workouts", status_code=302)

@router.post("/delete/{workout_id}", response_class=HTMLResponse)
async def delete_workout_route(request: Request, workout_id: int, user: User = Depends(get_current_user)):
    if isinstance(user, StarletteRedirectResponse):
        return user
    try:
        workout = await get_workout_by_id(workout_id)
        if not workout or workout.user_id != user.id:
            request.session["error"] = "Тренировка не найдена или доступ запрещён."
            return RedirectResponse("/workouts", status_code=302)
        await delete_workout(workout_id)
        request.session["success"] = "Тренировка успешно удалена!"
    except Exception as e:
        request.session["error"] = f"Ошибка: {str(e)}"
    return RedirectResponse("/workouts", status_code=302)