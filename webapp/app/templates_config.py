from fastapi.templating import Jinja2Templates
from pathlib import Path

# Настраиваем пути к шаблонам
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates")) 