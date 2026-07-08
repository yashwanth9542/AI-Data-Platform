from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health() -> dict[str, str]:
    print("[backend] /health endpoint reached")
    return {"status": "ok", "provider": settings.default_llm_provider, "database": settings.default_database}
