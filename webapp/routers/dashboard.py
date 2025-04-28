# webapp/routers/dashboard.py

import io
from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

import matplotlib.pyplot as plt
from services.db import get_progress, get_workouts

router = APIRouter()
templates = Jinja2Templates(directory="webapp/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    # здесь вы могли получать user_id через request.state или из сессии,
    # я покажу пример с фиктивным user_id=1
    weight_rows = await get_progress(user_id=1, metric="weight", limit=10)
    workouts = await get_workouts(user_id=1, limit=10)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "weight_rows": weight_rows,
        "workouts": workouts,
    })

@router.get("/plot/weight")
async def plot_weight():
    rows = await get_progress(user_id=1, metric="weight", limit=30)
    if not rows:
        return Response(status_code=204)

    dates = [r[3].split(".")[0] for r in rows][::-1]
    values = [r[2] for r in rows][::-1]

    plt.figure()
    plt.plot(dates, values)
    plt.xticks(rotation=45)
    plt.title("Прогресс веса")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
