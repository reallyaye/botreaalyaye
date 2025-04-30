from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from services.db import get_weights, add_weight

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def require_user_id(user_id: int = None):
    if not user_id:
        raise HTTPException(400, "user_id is required")
    return user_id

@router.get("/weight", response_class=HTMLResponse)
async def view_weights(request: Request, user_id: int = Depends(require_user_id)):
    rows = await get_weights(user_id)
    return templates.TemplateResponse("weight.html", {
        "request": request,
        "weights": rows,
        "user_id": user_id
    })

@router.post("/weight/add")
async def add_new_weight(
    user_id: int    = Form(...),
    weight: float   = Form(...)
):
    await add_weight(user_id, weight)
    return RedirectResponse(f"/weight?user_id={user_id}", status_code=302)
