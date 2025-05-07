from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from starlette.responses import RedirectResponse as StarletteRedirectResponse
from webapp.app.services.db import AsyncSessionLocal, Workout, get_user_by_id, get_user_stats, get_weekly_stats, get_monthly_stats, get_monthly_activity_trend, User
from datetime import datetime, timedelta
import secrets

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

@router.get("/", response_class=HTMLResponse)
async def stats(request: Request, user: User = Depends(get_current_user), period: str = "all"):
    # Проверяем, является ли user перенаправлением
    if isinstance(user, StarletteRedirectResponse):
        return user

    # Генерируем CSRF-токен
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_hex(16)
    
    # Получаем статистику за разные периоды
    all_time_stats = await get_user_stats(user.id)
    weekly_stats = await get_weekly_stats(user.id)
    monthly_stats = await get_monthly_stats(user.id)
    monthly_trend = await get_monthly_activity_trend(user.id)

    # Отладочный вывод
    print(f"all_time_stats: {all_time_stats}")
    print(f"weekly_stats: {weekly_stats}")
    print(f"monthly_stats: {monthly_stats}")
    print(f"monthly_trend: {monthly_trend}")

    # Определяем статистику в зависимости от выбранного периода
    if period == "week":
        selected_stats = weekly_stats
        period_label = "за последнюю неделю"
        start_date = datetime.utcnow() - timedelta(days=7)
    elif period == "month":
        selected_stats = monthly_stats
        period_label = "за последний месяц"
        start_date = datetime.utcnow() - timedelta(days=30)
    else:
        selected_stats = all_time_stats
        period_label = "за всё время"
        start_date = None

    # Получаем разбивку по активностям за выбранный период
    activity_breakdown = []
    async with AsyncSessionLocal() as session:
        if start_date:
            activities_result = await session.execute(
                select(Workout.activity, func.sum(Workout.duration).label("total_duration"))
                .where(Workout.user_id == user.id)
                .where(Workout.created_at >= start_date)
                .group_by(Workout.activity)
            )
        else:
            activities_result = await session.execute(
                select(Workout.activity, func.sum(Workout.duration).label("total_duration"))
                .where(Workout.user_id == user.id)
                .group_by(Workout.activity)
            )
        activity_breakdown = [{"activity": row.activity, "duration": row.total_duration or 0} for row in activities_result.fetchall()]

    # Отладочный вывод
    print(f"activity_breakdown: {activity_breakdown}")

    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "username": user.username,
            "is_authenticated": True,
            "all_time_stats": all_time_stats,
            "weekly_stats": weekly_stats,
            "monthly_stats": monthly_stats,
            "selected_stats": selected_stats if selected_stats else {"total_workouts": 0, "total_minutes": 0, "total_calories": 0},
            "period_label": period_label if period_label else "за всё время",
            "activity_breakdown": activity_breakdown if activity_breakdown else [],
            "monthly_trend": monthly_trend if monthly_trend else [],
            "period": period,
            "csrf_token": request.session.get("csrf_token")
        }
    )