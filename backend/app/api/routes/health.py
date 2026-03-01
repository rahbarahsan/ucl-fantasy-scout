"""Health-check endpoint."""

from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return basic health status and provider availability."""
    return {
        "status": "ok",
        "environment": settings.environment,
        "anthropic_configured": "yes" if settings.has_anthropic_key() else "no",
        "gemini_configured": "yes" if settings.has_gemini_key() else "no",
    }
