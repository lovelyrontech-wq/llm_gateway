from pathlib import Path

from fastapi.templating import Jinja2Templates

VIEWS_DIR = Path(__file__).parent
STATIC_DIR = VIEWS_DIR / "static"
templates = Jinja2Templates(directory=VIEWS_DIR / "templates")
