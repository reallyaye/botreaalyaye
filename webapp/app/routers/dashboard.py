from fastapi import APIRouter, Request, Depends, Form, Path, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from starlette.responses import RedirectResponse as StarletteRedirectResponse
from webapp.app.services.db import AsyncSessionLocal, Workout, get_user_by_id, get_weekly_stats, User, get_user_stats, Goal, get_user_schedules, add_schedule, get_workout_by_id, update_workout, delete_schedule, get_user_goals, Schedule, add_workout
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
            tips.append("Попробуйте приседания с утяжелениям, чтобы усилить эффект от тренировок.")
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

@router.post("/add-schedule", response_class=JSONResponse)
async def add_schedule_route(request: Request, activity: str = Form(...), scheduled_time: str = Form(...)):
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Пользователь не авторизован."})
    try:
        scheduled_dt = datetime.strptime(scheduled_time, "%Y-%m-%dT%H:%M")
        await add_schedule(user_id, activity, scheduled_dt)
        request.session["success"] = "Тренировка успешно запланирована!"
        return JSONResponse(status_code=200, content={"status": "success", "message": "Тренировка успешно запланирована!"})
    except ValueError:
        request.session["error"] = "Некорректная дата/время."
        return JSONResponse(status_code=400, content={"status": "error", "message": "Некорректная дата/время."})
    except Exception as e:
        print(f"Ошибка при добавлении расписания: {e}")
        request.session["error"] = "Произошла ошибка при планировании тренировки."
        return JSONResponse(status_code=500, content={"status": "error", "message": "Произошла ошибка при планировании тренировки."})

@router.post("/delete-schedule/{schedule_id}")
async def delete_schedule_route(request: Request, schedule_id: int = Path(...)):
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Пользователь не авторизован."})
    await delete_schedule(schedule_id, user_id)
    return JSONResponse({"success": True})

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

@router.post("/edit-schedule/{schedule_id}")
async def edit_schedule_submit(request: Request, schedule_id: int = Path(...), activity: str = Form(...), scheduled_time: str = Form(...)):
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Пользователь не авторизован."})
    from datetime import datetime
    try:
        scheduled_dt = datetime.strptime(scheduled_time, "%Y-%m-%dT%H:%M")
    except ValueError as e:
        print(f"Ошибка при парсинге даты/времени: {e}")
        request.session["error"] = "Некорректная дата/время."
        return JSONResponse(status_code=400, content={"status": "error", "message": "Некорректная дата/время."})
    # Обновляем расписание
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Schedule).where(Schedule.id == schedule_id, Schedule.user_id == user_id))
            schedule = result.scalars().first()
            if schedule:
                schedule.activity = activity
                schedule.scheduled_time = scheduled_dt
                session.add(schedule)
                await session.commit()
                request.session["success"] = "Тренировка успешно обновлена!"
                return JSONResponse(status_code=200, content={"status": "success", "message": "Тренировка успешно обновлена!", "redirect_url": "/dashboard"})
            else:
                request.session["error"] = "Запланированная тренировка не найдена или доступ запрещён."
                return JSONResponse(status_code=404, content={"status": "error", "message": "Запланированная тренировка не найдена или доступ запрещён."})
    except Exception as e:
        print(f"Ошибка при обновлении запланированной тренировки: {e}")
        request.session["error"] = "Произошла ошибка при обновлении тренировки."
        return JSONResponse(status_code=500, content={"status": "error", "message": "Произошла ошибка при обновлении тренировки."})

@router.get("/upcoming-workouts", response_class=HTMLResponse)
async def upcoming_workouts_partial(request: Request, user: User = Depends(get_current_user)):
    upcoming_workouts = await get_user_schedules(user.id)
    return templates.TemplateResponse(
        "upcoming_workouts.html",
        {"request": request, "upcoming_workouts": upcoming_workouts}
    )

@router.get("/schedule-data/{schedule_id}")
async def get_schedule_data(schedule_id: int, user: User = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Schedule).where(Schedule.id == schedule_id, Schedule.user_id == user.id))
        schedule = result.scalars().first()
        if not schedule:
            return JSONResponse(status_code=404, content={"error": "Not found"})
        return {
            "id": schedule.id,
            "activity": schedule.activity,
            "scheduled_time": schedule.scheduled_time.strftime("%Y-%m-%dT%H:%M")
        }

@router.post("/start-schedule/{schedule_id}")
async def start_schedule(schedule_id: int, request: Request, user: User = Depends(get_current_user)):
    if isinstance(user, StarletteRedirectResponse):
        return JSONResponse(status_code=401, content={"status": "error", "message": "Пользователь не авторизован."})
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Schedule).where(Schedule.id == schedule_id, Schedule.user_id == user.id))
            schedule = result.scalars().first()
            
            if not schedule:
                return JSONResponse({"status": "error", "message": "Запланированная тренировка не найдена."}, status_code=404)

            # Добавляем тренировку в историю завершенных тренировок
            # Предполагаем, что для 'старта' тренировки интенсивность будет 'Обычная', длительность - 30 минут (можно потом отредактировать)
            # А комментарий - название запланированной тренировки.
            await add_workout(user.id, schedule.activity, "Обычная", 30.0, f"Начата запланированная тренировка: {schedule.activity}")

            # Удаляем тренировку из запланированных
            await delete_schedule(schedule.id, user.id)

            request.session["success"] = "Тренировка успешно начата и добавлена в историю!"
            return JSONResponse({"status": "success", "message": "Тренировка успешно начата!", "redirect_url": "/dashboard"})
    except Exception as e:
        print(f"Ошибка при начале запланированной тренировки: {e}")
        request.session["error"] = "Произошла ошибка при начале тренировки."
        return JSONResponse({"status": "error", "message": "Произошла ошибка при начале тренировки."}, status_code=500)

@router.post("/finish-schedule/{schedule_id}")
async def finish_schedule(schedule_id: int, request: Request, user: User = Depends(get_current_user)):
    data = await request.json()
    duration_seconds = data.get('duration_seconds')
    if not duration_seconds:
        return JSONResponse(status_code=400, content={"error": "No duration"})
    async with AsyncSessionLocal() as session:
        # Получаем расписание
        result = await session.execute(select(Schedule).where(Schedule.id == schedule_id, Schedule.user_id == user.id))
        schedule = result.scalars().first()
        if not schedule:
            return JSONResponse(status_code=404, content={"error": "Not found"})
        # Сохраняем тренировку
        duration_min = round(duration_seconds / 60, 2)
        await add_workout(user.id, schedule.activity, intensity="Обычная", duration=duration_min)
        # Удаляем из расписания
        await session.delete(schedule)
        await session.commit()
    return JSONResponse({"success": True})

@router.get("/stats-json")
async def stats_json(request: Request, user: User = Depends(get_current_user)):
    all_time_stats = await get_user_stats(user.id)
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(func.count()).select_from(Goal).where(Goal.user_id == user.id).where(Goal.achieved == True)
        )
        achievements_count = result.scalar() or 0
    return {
        "total_workouts": all_time_stats["total_workouts"],
        "total_minutes": all_time_stats["total_minutes"],
        "total_calories": all_time_stats["total_calories"],
        "achievements_count": achievements_count
    }

async def delete_schedule(schedule_id: int, user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Schedule).where(Schedule.id == schedule_id, Schedule.user_id == user_id))
        schedule = result.scalars().first()
        if schedule:
            await session.delete(schedule)
            await session.commit()
            print(f"DEBUG: Successfully deleted schedule ID {schedule_id} for user {user_id}")
        else:
            print(f"DEBUG: Attempted to delete non-existent or unauthorized schedule ID {schedule_id} for user {user_id}")

async def get_pending_reminders():
    async with AsyncSessionLocal() as session:
        current_time = datetime.now()
        result = await session.execute(
            select(Schedule)
            .where(Schedule.scheduled_time > current_time)
            .order_by(Schedule.scheduled_time)
        )
        return result.scalars().all()