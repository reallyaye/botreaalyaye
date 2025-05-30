from fastapi import APIRouter, Request, Depends, Form, Path
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from starlette.responses import RedirectResponse as StarletteRedirectResponse
from webapp.app.services.db import AsyncSessionLocal, Workout, get_user_by_id, get_weekly_stats, User, get_user_stats, Goal, get_user_schedules, add_schedule, get_workout_by_id, update_workout, delete_schedule, get_user_goals
from datetime import datetime, timedelta

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
async def dashboard(request: Request, user: User = Depends(get_current_user)):
    if isinstance(user, StarletteRedirectResponse):
        return user
    
    # Получаем статистику за последние 7 дней
    weekly_stats = await get_weekly_stats(user.id)

    # Получаем статистику за предыдущую неделю для сравнения
    start_date_prev = datetime.utcnow() - timedelta(days=14)
    end_date_prev = datetime.utcnow() - timedelta(days=7)
    prev_week_stats = await get_weekly_stats(user.id)
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(
                func.count().label("total_workouts"),
                func.sum(Workout.duration).label("total_minutes")
            )
            .where(Workout.user_id == user.id)
            .where(Workout.created_at >= start_date_prev)
            .where(Workout.created_at < end_date_prev)
        )
        prev_stats = result.first()
        prev_week_stats = {
            "total_workouts": prev_stats.total_workouts or 0,
            "total_minutes": prev_stats.total_minutes or 0
        }

    # Получаем статистику за всё время
    all_time_stats = await get_user_stats(user.id)

    # Получаем количество достижений (если есть таблица Achievement)
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(func.count()).select_from(Goal).where(Goal.user_id == user.id).where(Goal.achieved == True)
        )
        achievements_count = result.scalar() or 0

    # Получаем предстоящие тренировки
    upcoming_workouts = await get_user_schedules(user.id)

    # Получаем цели пользователя
    user_goals = await get_user_goals(user.id)

    # Формируем мотивационное сообщение с учётом прогресса
    motivation_message = "Начните тренироваться, чтобы достичь своих целей!"
    if weekly_stats["total_workouts"] > 0:
        if weekly_stats["total_workouts"] > prev_week_stats["total_workouts"]:
            motivation_message = f"Отличный прогресс, {user.username}! Вы провели {weekly_stats['total_workouts']} тренировок на этой неделе, это больше, чем на прошлой (всего {prev_week_stats['total_workouts']})!"
        else:
            motivation_message = f"Хорошая работа, {user.username}! Вы провели {weekly_stats['total_workouts']} тренировок на этой неделе. Продолжайте в том же духе!"

    # Генерируем несколько советов на основе активности
    tips = ["Не забывайте пить воду во время тренировок и делать разминку перед началом!"]
    if weekly_stats["top_activities"]:
        top_activity = weekly_stats["top_activities"][0]["activity"].lower()
        if "бег" in top_activity:
            tips.append("Попробуйте интервальный бег, чтобы улучшить выносливость.")
            tips.append("Носите удобные кроссовки, чтобы избежать травм при беге.")
        elif "йога" in top_activity:
            tips.append("Добавьте дыхательные упражнения в свою йогу для большего расслабления.")
            tips.append("Практикуйте йогу утром, чтобы зарядиться энергией на весь день.")
        elif "приседания" in top_activity:
            tips.append("Попробуйте приседания с утяжелением, чтобы усилить эффект от тренировок.")
            tips.append("Следите за техникой: держите спину прямо во время приседаний.")
        elif "планка" in top_activity:
            tips.append("Увеличьте время удержания планки на 10 секунд каждую неделю для прогресса.")
            tips.append("Попробуйте боковую планку для разнообразия.")
    else:
        tips.append("Попробуйте разные виды активности, чтобы найти то, что вам нравится.")
        tips.append("Ставьте небольшие цели, например, 3 тренировки в неделю.")

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "username": user.username,
            "is_authenticated": True,
            "weekly_stats": weekly_stats,
            "motivation_message": motivation_message,
            "tips": tips,
            "all_time_stats": all_time_stats,
            "achievements_count": achievements_count,
            "upcoming_workouts": upcoming_workouts,
            "user_goals": user_goals,
            "success": request.session.pop("success", None),
            "error": request.session.pop("error", None)
        }
    )

@router.post("/add-schedule", response_class=HTMLResponse)
async def add_schedule_route(request: Request, activity: str = Form(...), scheduled_time: str = Form(...)):
    user_id = request.session.get("user_id")
    if not user_id:
        return StarletteRedirectResponse("/login", status_code=302)
    # Преобразуем строку времени в datetime
    try:
        scheduled_dt = datetime.strptime(scheduled_time, "%Y-%m-%dT%H:%M")
    except Exception:
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "error": "Некорректная дата/время"}
        )
    await add_schedule(user_id, activity, scheduled_dt)
    return StarletteRedirectResponse("/", status_code=302)

@router.post("/delete-schedule/{schedule_id}")
async def delete_schedule_route(request: Request, schedule_id: int = Path(...)):
    user_id = request.session.get("user_id")
    if not user_id:
        return StarletteRedirectResponse("/login", status_code=302)
    await delete_schedule(schedule_id)
    return StarletteRedirectResponse("/", status_code=302)

@router.get("/edit-schedule/{schedule_id}", response_class=HTMLResponse)
async def edit_schedule_form(request: Request, schedule_id: int = Path(...)):
    user_id = request.session.get("user_id")
    if not user_id:
        return StarletteRedirectResponse("/login", status_code=302)
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Goal).where(Goal.id == schedule_id))
        schedule = result.scalars().first()
    return templates.TemplateResponse(
        "edit_schedule.html",
        {"request": request, "schedule": schedule}
    )

@router.post("/edit-schedule/{schedule_id}", response_class=HTMLResponse)
async def edit_schedule_submit(request: Request, schedule_id: int = Path(...), activity: str = Form(...), scheduled_time: str = Form(...)):
    user_id = request.session.get("user_id")
    if not user_id:
        return StarletteRedirectResponse("/login", status_code=302)
    from datetime import datetime
    try:
        scheduled_dt = datetime.strptime(scheduled_time, "%Y-%m-%dT%H:%M")
    except Exception:
        return templates.TemplateResponse(
            "edit_schedule.html",
            {"request": request, "error": "Некорректная дата/время"}
        )
    # Обновляем расписание
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Goal).where(Goal.id == schedule_id))
        schedule = result.scalars().first()
        if schedule:
            schedule.activity = activity
            schedule.scheduled_time = scheduled_dt
            session.add(schedule)
            await session.commit()
    return StarletteRedirectResponse("/", status_code=302)

@router.get("/upcoming-workouts", response_class=HTMLResponse)
async def upcoming_workouts_partial(request: Request, user: User = Depends(get_current_user)):
    upcoming_workouts = await get_user_schedules(user.id)
    return templates.TemplateResponse(
        "upcoming_workouts.html",
        {"request": request, "upcoming_workouts": upcoming_workouts}
    )