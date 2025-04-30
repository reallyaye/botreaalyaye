# webapp/routers/profile.py

from pathlib import Path

from fastapi import (
    APIRouter, Request,
    Depends, Form, Query, HTTPException
)
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from services.profile import (
    register_user as register_user_profile,
    get_user_profile,
    update_user_profile
)

# Шаблоны лежат в webapp/templates
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)

def require_user_id(user_id: int = Query(..., description="Telegram user_id")) -> int:
    """
    Достаём user_id из query, валидируем.
    Если не передан или не число — вернём 400.
    """
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id не задан")
    return user_id

@router.get("/", response_class=HTMLResponse)
async def view_profile(
    request: Request,
    user_id: int = Depends(require_user_id)
):
    """
    GET /profile/?user_id=12345
    Если профиля ещё нет — покажем форму регистрации,
    иначе — отобразим существующие данные.
    """
    # Зарегистрируем пользователя, если нет
    await register_user_profile({"id": user_id})

    profile = await get_user_profile(user_id)
    if not profile:
        # Показываем форму создания/обновления
        return templates.TemplateResponse("profile_form.html", {
            "request": request,
            "user_id": user_id
        })

    # Показываем профиль
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "profile": profile,
        "user_id": user_id
    })

@router.post("/update")
async def update_profile(
    user_id: int    = Form(...),
    first_name: str = Form(...),
    last_name: str  = Form(""),
    username: str   = Form("")
):
    """
    POST /profile/update
    Обновляем профиль и редиректим на GET /profile
    """
    await update_user_profile(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        username=username
    )
    return RedirectResponse(
        url=f"/profile?user_id={user_id}",
        status_code=303
    )
