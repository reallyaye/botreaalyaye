from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse as StarletteRedirectResponse
from webapp.app.services.db import get_user_by_id, add_goal, delete_goal, User
import secrets
from datetime import datetime, timedelta

router = APIRouter()
templates = Jinja2Templates(directory="webapp/app/templates")

async def get_current_user(request: Request):
    uid = request.session.get("user_id")
    if not uid:
        return StarletteRedirectResponse("/login", status_code=302)
    user = await get_user_by_id(uid)
    if not user:
        request.session.clear()
        return StarletteRedirectResponse("/login", status_code=302)
    return user

@router.get("/add", response_class=HTMLResponse)
async def add_goal_page(request: Request, user: User = Depends(get_current_user)):
    if isinstance(user, StarletteRedirectResponse):
        return user

    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_hex(16)

    return templates.TemplateResponse(
        "add_goal.html",
        {
            "request": request,
            "username": user.username,
            "is_authenticated": True,
            "success": request.session.pop("success", None),
            "error": request.session.pop("error", None),
            "csrf_token": request.session.get("csrf_token")
        }
    )

@router.post("/add", response_class=HTMLResponse)
async def add_goal_route(
    request: Request,
    user: User = Depends(get_current_user),
    goal_type: str = Form(...),
    target_value: float = Form(...),
    deadline: str = Form(...),
    csrf_token: str = Form(...)
):
    if isinstance(user, StarletteRedirectResponse):
        return user

    if csrf_token != request.session.get("csrf_token"):
        request.session["error"] = "Недействительный CSRF-токен."
        return RedirectResponse("/goals/add", status_code=302)

    if goal_type not in ["calories", "workouts", "duration"]:
        request.session["error"] = "Недопустимый тип цели."
        return RedirectResponse("/goals/add", status_code=302)

    if target_value <= 0:
        request.session["error"] = "Целевое значение должно быть больше 0."
        return RedirectResponse("/goals/add", status_code=302)

    try:
        deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
        if deadline_date < datetime.now():
            request.session["error"] = "Дедлайн должен быть в будущем."
            return RedirectResponse("/goals/add", status_code=302)
    except ValueError:
        request.session["error"] = "Неверный формат даты (ожидается ГГГГ-ММ-ДД)."
        return RedirectResponse("/goals/add", status_code=302)

    try:
        await add_goal(user.id, goal_type, target_value, deadline_date)
        request.session["success"] = "Цель успешно добавлена!"
    except Exception as e:
        print(f"Ошибка при добавлении цели: {e}")
        request.session["error"] = "Произошла ошибка при добавлении цели. Попробуйте снова."
    return RedirectResponse("/", status_code=302)

@router.post("/delete/{goal_id}", response_class=HTMLResponse)
async def delete_goal_route(request: Request, goal_id: int, user: User = Depends(get_current_user), csrf_token: str = Form(...)):
    if isinstance(user, StarletteRedirectResponse):
        return user

    if csrf_token != request.session.get("csrf_token"):
        request.session["error"] = "Недействительный CSRF-токен."
        return RedirectResponse("/", status_code=302)

    try:
        await delete_goal(goal_id)
        request.session["success"] = "Цель успешно удалена!"
    except Exception as e:
        print(f"Ошибка при удалении цели: {e}")
        request.session["error"] = "Произошла ошибка при удалении цели. Попробуйте снова."
    return RedirectResponse("/", status_code=302)

@router.post("/add-json")
async def add_goal_json(
    request: Request,
    user: User = Depends(get_current_user),
    goal_type: str = Form(...),
    target_value: float = Form(...),
    deadline: str = Form(...),
    csrf_token: str = Form(...)
):
    if csrf_token != request.session.get("csrf_token"):
        return JSONResponse(status_code=400, content={"status": "error", "message": "Недействительный CSRF-токен."})
    if goal_type not in ["calories", "workouts", "duration"]:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Недопустимый тип цели."})
    if target_value <= 0:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Целевое значение должно быть больше 0."})
    try:
        deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
        if deadline_date < datetime.now():
            return JSONResponse(status_code=400, content={"status": "error", "message": "Дедлайн должен быть в будущем."})
    except ValueError:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Неверный формат даты (ожидается ГГГГ-ММ-ДД)."})
    try:
        await add_goal(user.id, goal_type, target_value, deadline_date)
        return JSONResponse(status_code=200, content={"status": "success", "message": "Цель успешно добавлена!"})
    except Exception as e:
        print(f"Ошибка при добавлении цели: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": "Произошла ошибка при добавлении цели. Попробуйте снова."})

@router.post("/delete-json/{goal_id}")
async def delete_goal_json(request: Request, goal_id: int, user: User = Depends(get_current_user), csrf_token: str = Form(...)):
    if csrf_token != request.session.get("csrf_token"):
        return JSONResponse(status_code=400, content={"status": "error", "message": "Недействительный CSRF-токен."})
    try:
        await delete_goal(goal_id)
        return JSONResponse(status_code=200, content={"status": "success", "message": "Цель успешно удалена!"})
    except Exception as e:
        print(f"Ошибка при удалении цели: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": "Произошла ошибка при удалении цели. Попробуйте снова."})

@router.get("/list", response_class=HTMLResponse)
async def goals_list_partial(request: Request, user: User = Depends(get_current_user)):
    user_goals = await user.get_goals() if hasattr(user, 'get_goals') else []
    # Если get_user_goals доступна, используйте её:
    try:
        from webapp.app.services.db import get_user_goals
        user_goals = await get_user_goals(user.id)
    except Exception:
        pass
    return templates.TemplateResponse(
        "goals_list_partial.html",
        {"request": request, "user_goals": user_goals}
    )