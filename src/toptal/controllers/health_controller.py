from fastapi import APIRouter

from toptal.config import get_settings
from toptal.models.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    s = get_settings()
    return HealthResponse(
        status="ok",
        default_provider=s.llm_provider,
        configured_providers=s.configured_providers(),
    )
