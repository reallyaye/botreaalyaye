from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from services.programs import list_goals, list_types, get_program
from services.db       import (
    get_custom_programs,
    add_custom_program,
    delete_custom_program,
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def require_user_id(user_id: int = None):
    if not user_id:
        raise HTTPException(400, "user_id is required")
    return user_id

@router.get("/programs", response_class=HTMLResponse)
async def choose_program(request: Request, user_id: int = Depends(require_user_id)):
    return templates.TemplateResponse("programs.html", {
        "request": request,
        "goals": list_goals(),
        "user_id": user_id
    })

@router.post("/programs/generate", response_class=HTMLResponse)
async def generate_program(
    request: Request,
    user_id: int = Form(...),
    goal: str    = Form(...),
    p_type: str  = Form(...)
):
    program = get_program(goal, p_type)
    return templates.TemplateResponse("programs_result.html", {
        "request": request,
        "program": program or {},
        "user_id": user_id
    })

@router.get("/programs/custom", response_class=HTMLResponse)
async def list_custom(request: Request, user_id: int = Depends(require_user_id)):
    progs = await get_custom_programs(user_id)
    return templates.TemplateResponse("custom_programs.html", {
        "request": request,
        "programs": progs,
        "user_id": user_id
    })

@router.post("/programs/custom/add")
async def add_custom(request: Request,
    user_id: int = Form(...),
    prog: str    = Form(...)
):
    await add_custom_program(user_id, prog)
    return RedirectResponse(f"/programs/custom?user_id={user_id}", status_code=302)

@router.post("/programs/custom/delete")
async def delete_custom(request: Request,
    user_id: int = Form(...),
    prog_id: int = Form(...)
):
    await delete_custom_program(user_id, prog_id)
    return RedirectResponse(f"/programs/custom?user_id={user_id}", status_code=302)
