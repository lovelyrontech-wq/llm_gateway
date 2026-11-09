from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from toptal.config import PROVIDERS, get_settings
from toptal.views.templates import templates

router = APIRouter(include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    s = get_settings()
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "title": "LLM Chat",
            "default_provider": s.llm_provider,
            "providers": PROVIDERS,
        },
    )
