from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="webapp/templates")

@router.get("/")
async def home(request: Request):
    user_id = request.query_params.get("user_id", "")
    return templates.TemplateResponse("home.html", {"request": request, "user_id": user_id})
