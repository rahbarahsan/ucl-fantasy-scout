"""API key validation middleware."""

from typing import Optional

from fastapi import HTTPException, Request

from app.config import settings
from app.utils.encryption import decrypt
from app.utils.logger import get_logger

logger = get_logger(__name__)

_HEADER_NAME = "X-API-Key"
_PROVIDER_HEADER = "X-Provider"


def resolve_api_key(
    request: Request,
    provider: str = "anthropic",
) -> Optional[str]:
    """Resolve the API key for the given provider.

    Priority:
    1. Encrypted key from request header ``X-API-Key``
    2. Server-side key from environment / ``.env``

    Returns ``None`` if no key is available.
    """
    # Try request header first (runtime user-supplied key)
    encrypted_key = request.headers.get(_HEADER_NAME)
    if encrypted_key:
        try:
            return decrypt(encrypted_key)
        except Exception:  # pylint: disable=broad-except
            logger.warning("api_key_decrypt_failed")

    # Fall back to server-side key
    if provider == "anthropic" and settings.has_anthropic_key():
        return settings.anthropic_api_key
    if provider == "gemini" and settings.has_gemini_key():
        return settings.gemini_api_key

    return None


def require_api_key(request: Request, provider: str = "anthropic") -> str:
    """Resolve and validate API key, raising HTTPException if unavailable."""
    api_key = resolve_api_key(request, provider=provider)
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail=(
                f"No {provider} API key available. "
                "Please configure it in settings or the server .env file."
            ),
        )
    return api_key
