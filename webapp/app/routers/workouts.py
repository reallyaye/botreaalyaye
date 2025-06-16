from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from starlette.responses import RedirectResponse as StarletteRedirectResponse
from webapp.app.services.db import AsyncSessionLocal, Workout, get_user_by_id, add_workout, delete_workout, get_all_user_workouts, get_workout_by_id, update_workout, User
import os
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
import secrets
from datetime import datetime

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
    # Проверяем, является ли user перенаправлением
    if isinstance(user, StarletteRedirectResponse):
        return user

    # Генерируем CSRF-токен
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_hex(16)

    workouts = await get_all_user_workouts(user.id)
    # Форматируем даты для каждой тренировки
    formatted_workouts = []
    for workout in workouts:
        formatted_workout = {
            "id": workout.id,
            "activity": workout.activity,
            "intensity": workout.intensity,
            "duration": workout.duration,
            "calories_burned": workout.calories_burned,
            "comment": workout.comment,
            "created_at": workout.created_at.strftime("%d.%m.%Y %H:%M") if workout.created_at else ""
        }
        formatted_workouts.append(formatted_workout)
    print(f"Форматированные тренировки: {formatted_workouts}")  # Отладочный вывод
    return templates.TemplateResponse(
        "workouts.html",
        {
            "request": request,
            "user_id": user.id,
            "username": user.username,
            "is_authenticated": True,
            "success": request.session.pop("success", None),
            "error": request.session.pop("error", None),
            "workouts": formatted_workouts,
            "csrf_token": request.session.get("csrf_token")
        }
    )

@router.post("/add", response_class=HTMLResponse)
async def add_workout_route(
    request: Request,
    user: User = Depends(get_current_user),
    activity: str = Form(...),
    intensity: str = Form(...),
    duration: float = Form(...),
    comment: str = Form(None),
    csrf_token: str = Form(...)
):
    if isinstance(user, StarletteRedirectResponse):
        return user

    if csrf_token != request.session.get("csrf_token"):
        request.session["error"] = "Недействительный CSRF-токен."
        return RedirectResponse("/workouts", status_code=302)
    if not activity.strip() or not intensity.strip():
        request.session["error"] = "Активность и интенсивность не могут быть пустыми."
        return RedirectResponse("/workouts", status_code=302)
    if duration <= 0:
        request.session["error"] = "Длительность должна быть больше 0."
        return RedirectResponse("/workouts", status_code=302)
    try:
        await add_workout(user.id, activity, intensity, duration, comment)
        # Получаем добавленную тренировку для получения calories_burned
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Workout)
                .where(Workout.user_id == user.id)
                .where(Workout.activity == activity)
                .where(Workout.intensity == intensity)
                .where(Workout.duration == duration)
                .order_by(Workout.created_at.desc())
                .limit(1)
            )
            workout = result.scalars().first()
        
        # Отправка уведомления в Telegram
        if user.telegram_id and workout:
            bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"), session=AiohttpSession())
            await bot.send_message(
                chat_id=user.telegram_id,
                text=f"Новая тренировка добавлена!\nАктивность: {activity}\nИнтенсивность: {intensity}\nДлительность: {duration} мин.\nКалорий сожжено: {workout.calories_burned:.2f}",
                parse_mode=ParseMode.HTML
            )
            await bot.session.close()
        request.session["success"] = "Тренировка успешно добавлена!"
    except Exception as e:
        print(f"Ошибка при добавлении тренировки: {e}")
        request.session["error"] = "Произошла ошибка при добавлении тренировки. Попробуйте снова."
    return RedirectResponse("/workouts", status_code=302)

@router.get("/edit/{workout_id}", response_class=HTMLResponse)
async def edit_workout_page(request: Request, workout_id: int, user: User = Depends(get_current_user)):
    if isinstance(user, StarletteRedirectResponse):
        return user

    # Генерируем CSRF-токен
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_hex(16)

    workout = await get_workout_by_id(workout_id)
    if not workout or workout.user_id != user.id:
        request.session["error"] = "Тренировка не найдена или доступ запрещён."
        return RedirectResponse("/workouts", status_code=302)
    workouts = await get_all_user_workouts(user.id)
    # Форматируем даты для списка тренировок
    formatted_workouts = []
    for w in workouts:
        formatted_workout = {
            "id": w.id,
            "activity": w.activity,
            "intensity": w.intensity,
            "duration": w.duration,
            "calories_burned": w.calories_burned,
            "comment": w.comment,
            "created_at": w.created_at.strftime("%d.%m.%Y %H:%M") if w.created_at else ""
        }
        formatted_workouts.append(formatted_workout)
    print(f"Форматированные тренировки для редактирования: {formatted_workouts}")  # Отладочный вывод
    return templates.TemplateResponse(
        "workouts.html",
        {
            "request": request,
            "user_id": user.id,
            "username": user.username,
            "is_authenticated": True,
            "success": request.session.pop("success", None),
            "error": request.session.pop("error", None),
            "workouts": formatted_workouts,
            "edit_workout": workout,
            "csrf_token": request.session.get("csrf_token")
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
    comment: str = Form(None),
    csrf_token: str = Form(...)
):
    if isinstance(user, StarletteRedirectResponse):
        return user

    if csrf_token != request.session.get("csrf_token"):
        request.session["error"] = "Недействительный CSRF-токен."
        return RedirectResponse("/workouts", status_code=302)
    workout = await get_workout_by_id(workout_id)
    if not workout or workout.user_id != user.id:
        request.session["error"] = "Тренировка не найдена или доступ запрещён."
        return RedirectResponse("/workouts", status_code=302)
    if not activity.strip() or not intensity.strip():
        request.session["error"] = "Активность и интенсивность не могут быть пустыми."
        return RedirectResponse("/workouts", status_code=302)
    if duration <= 0:
        request.session["error"] = "Длительность должна быть больше 0."
        return RedirectResponse("/workouts", status_code=302)
    try:
        await update_workout(workout_id, activity, intensity, duration, comment)
        # Получаем обновлённую тренировку для получения calories_burned
        updated_workout = await get_workout_by_id(workout_id)
        
        # Отправка уведомления в Telegram
        if user.telegram_id and updated_workout:
            bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"), session=AiohttpSession())
            await bot.send_message(
                chat_id=user.telegram_id,
                text=f"Тренировка обновлена!\nАктивность: {activity}\nИнтенсивность: {intensity}\nДлительность: {duration} мин.\nКалорий сожжено: {updated_workout.calories_burned:.2f}",
                parse_mode=ParseMode.HTML
            )
            await bot.session.close()
        request.session["success"] = "Тренировка успешно обновлена!"
    except Exception as e:
        print(f"Ошибка при обновлении тренировки: {e}")
        request.session["error"] = "Произошла ошибка при обновлении тренировки. Попробуйте снова."
    return RedirectResponse("/workouts", status_code=302)

@router.post("/delete/{workout_id}", response_class=HTMLResponse)
async def delete_workout_route(request: Request, workout_id: int, user: User = Depends(get_current_user), csrf_token: str = Form(...)):
    if isinstance(user, StarletteRedirectResponse):
        return user

    if csrf_token != request.session.get("csrf_token"):
        request.session["error"] = "Недействительный CSRF-токен."
        return RedirectResponse("/workouts", status_code=302)
    try:
        workout = await get_workout_by_id(workout_id)
        if not workout or workout.user_id != user.id:
            request.session["error"] = "Тренировка не найдена или доступ запрещён."
            return RedirectResponse("/workouts", status_code=302)
        await delete_workout(workout_id)
        request.session["success"] = "Тренировка успешно удалена!"
    except Exception as e:
        print(f"Ошибка при удалении тренировки: {e}")
        request.session["error"] = "Произошла ошибка при удалении тренировки. Попробуйте снова."
    return RedirectResponse("/workouts", status_code=302)

@router.get("/edit/{workout_id}")
async def get_workout_json(request: Request, workout_id: int, user: User = Depends(get_current_user)):
    workout = await get_workout_by_id(workout_id)
    if not workout or workout.user_id != user.id:
        return JSONResponse(status_code=404, content={"error": "Not found"})
    return JSONResponse({
        "id": workout.id,
        "activity": workout.activity,
        "intensity": workout.intensity,
        "duration": workout.duration,
        "calories_burned": workout.calories_burned,
        "comment": workout.comment,
        "created_at": workout.created_at.strftime("%d.%m.%Y %H:%M") if workout.created_at else ""
    })

@router.post("/add")
async def add_workout_ajax(request: Request, user: User = Depends(get_current_user)):
    form = await request.form()
    activity = form.get("activity")
    intensity = form.get("intensity")
    duration = float(form.get("duration"))
    comment = form.get("comment")
    await add_workout(user.id, activity, intensity, duration, comment)
    return JSONResponse({"success": True})

@router.post("/edit/{workout_id}")
async def edit_workout_ajax(request: Request, workout_id: int, user: User = Depends(get_current_user)):
    form = await request.form()
    activity = form.get("activity")
    intensity = form.get("intensity")
    duration = float(form.get("duration"))
    comment = form.get("comment")
    await update_workout(workout_id, activity, intensity, duration, comment)
    return JSONResponse({"success": True})

@router.post("/delete/{workout_id}")
async def delete_workout_ajax(request: Request, workout_id: int, user: User = Depends(get_current_user)):
    workout = await get_workout_by_id(workout_id)
    if not workout or workout.user_id != user.id:
        return JSONResponse(status_code=404, content={"error": "Not found"})
    await delete_workout(workout_id)
    return JSONResponse({"success": True})

@router.get("/list-partial", response_class=HTMLResponse)
async def workouts_list_partial(request: Request, user: User = Depends(get_current_user)):
    workouts = await get_all_user_workouts(user.id)
    formatted_workouts = []
    for workout in workouts:
        formatted_workout = {
            "id": workout.id,
            "activity": workout.activity,
            "intensity": workout.intensity,
            "duration": workout.duration,
            "calories_burned": workout.calories_burned,
            "comment": workout.comment,
            "created_at": workout.created_at.strftime("%d.%m.%Y %H:%M") if workout.created_at else ""
        }
        formatted_workouts.append(formatted_workout)
    return templates.TemplateResponse(
        "workouts_list_partial.html",
        {"request": request, "workouts": formatted_workouts}
    )

@router.post("/start-suggested", response_class=JSONResponse)
async def start_suggested_workout_route(
    request: Request,
    user: User = Depends(get_current_user),
    activity: str = Form(...),
    intensity: str = Form(...),
    duration: float = Form(None),
    comment: str = Form(None),
    csrf_token: str = Form(...)
):
    if isinstance(user, StarletteRedirectResponse):
        return user

    if csrf_token != request.session.get("csrf_token"):
        return JSONResponse({"status": "error", "message": "Недействительный CSRF-токен."}, status_code=400)

    if not activity.strip() or not intensity.strip():
        return JSONResponse({"status": "error", "message": "Активность и интенсивность не могут быть пустыми."}, status_code=400)
    
    # Set default duration if not provided (e.g., 5 minutes for a quick start)
    if duration is None or duration <= 0:
        duration = 5.0 # Default duration for starting a suggested workout

    try:
        await add_workout(user.id, activity, intensity, duration, comment)
        # We can fetch the added workout to get calories_burned if needed for the response
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Workout)
                .where(Workout.user_id == user.id)
                .where(Workout.activity == activity)
                .where(Workout.intensity == intensity)
                .where(Workout.duration == duration)
                .order_by(Workout.created_at.desc())
                .limit(1)
            )
            workout = result.scalars().first()

        # Send Telegram notification (optional, based on existing logic)
        if user.telegram_id and workout:
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            if bot_token:
                bot = Bot(token=bot_token, session=AiohttpSession())
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=f"Начата новая тренировка!\nАктивность: {activity}\nИнтенсивность: {intensity}\nДлительность: {duration} мин.",
                    parse_mode=ParseMode.HTML
                )
                await bot.session.close()

        return JSONResponse({"status": "success", "message": "Тренировка успешно начата!", "redirect_url": "/dashboard"})
    except Exception as e:
        print(f"Ошибка при начале тренировки: {e}")
        return JSONResponse({"status": "error", "message": "Произошла ошибка при начале тренировки. Попробуйте снова."}, status_code=500)