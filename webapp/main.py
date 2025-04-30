from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from services.db import init_db, get_workouts, add_workout
from services.profile import get_user_profile

app = FastAPI()

# Авто-создаём sqlite и таблицы при старте
@app.on_event("startup")
async def startup():
    await init_db()

# Статика и шаблоны
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Главная страница. Пользователь ещё не зашёл по ссылке с user_id.
    Предлагаем в URL добавить ?user_id=ваш_ID.
    """
    return templates.TemplateResponse("home.html", {
        "request": request
    })


def require_user(user_id: int = None):
    if not user_id:
        raise HTTPException(400, "Не задан user_id в URL")
    return user_id


@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, user_id: int = Depends(require_user)):
    """
    /profile?user_id=1027288917
    """
    prof = await get_user_profile(user_id)
    if not prof:
        raise HTTPException(404, "Профиль не найден")
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "profile": prof
    })


@app.get("/workouts", response_class=HTMLResponse)
async def workouts_list(request: Request, user_id: int = Depends(require_user)):
    """
    Список последних 10 тренировок.
    """
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
    details: str = Form("")  # «сложность…, вес…, детали»
):
    """
    Форма добавления тренировки с главной страницы /workouts
    """
    await add_workout(
        user_id=user_id,
        workout_type=workout_type,
        duration=duration,
        details=details
    )
    # после добавления — редирект обратно на список
    return RedirectResponse(f"/workouts?user_id={user_id}", status_code=302)
