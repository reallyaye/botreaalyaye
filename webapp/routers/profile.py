from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from services.profile import get_user_profile, update_user_profile

router = APIRouter()
templates = Jinja2Templates(directory="webapp/templates")

@router.get("/")
async def view_profile(request: Request):
    user_id = request.query_params.get("user_id")
    if not user_id:
        return templates.TemplateResponse("error.html", {"request": request, "msg": "user_id не задан"})
    uid = int(user_id)
    profile = await get_user_profile(uid)
    if profile is None:
        return templates.TemplateResponse("error.html", {"request": request, "msg": "Профиль не найден"})
    return templates.TemplateResponse("profile.html", {"request": request, "profile": profile, "user_id": uid})

@router.post("/update")
async def update_profile(request: Request, user_id: int = Form(...),
                         first_name: str | None = Form(None),
                         last_name: str | None = Form(None),
                         username: str | None = Form(None)):
    await update_user_profile(user_id, username=username, first_name=first_name, last_name=last_name)
    return RedirectResponse(f"/profile/?user_id={user_id}", status_code=303)
