"""API key validation middleware."""

from typing import Optional

from fastapi import Request

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
