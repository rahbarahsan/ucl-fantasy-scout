"""Image processing utilities — Base64 handling and validation."""

import base64
import io
from typing import Optional

from PIL import Image

from app.utils.logger import get_logger

logger = get_logger(__name__)

ALLOWED_FORMATS = {"png", "jpeg", "gif", "webp"}
MAX_IMAGE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


def validate_base64_image(data: str) -> Optional[str]:
    """Validate a Base64-encoded image string.

    Returns the image format (e.g. ``"png"``) on success, or ``None`` if
    the data is invalid or the format is not supported.
    """
    try:
        # Strip optional data-URI prefix
        if "," in data:
            data = data.split(",", 1)[1]
        raw = base64.b64decode(data, validate=True)
    except Exception:  # pylint: disable=broad-except
        logger.warning("base64_decode_failed")
        return None

    if len(raw) > MAX_IMAGE_SIZE_BYTES:
        logger.warning("image_too_large", size=len(raw))
        return None

    try:
        img = Image.open(io.BytesIO(raw))
        fmt = img.format.lower() if img.format else None
    except Exception:  # pylint: disable=broad-except
        logger.warning("invalid_image_data")
        return None

    if fmt not in ALLOWED_FORMATS:
        logger.warning("unsupported_image_format", format=fmt)
        return None

    return fmt


def strip_data_uri(data: str) -> str:
    """Remove the ``data:image/…;base64,`` prefix if present."""
    if "," in data:
        return data.split(",", 1)[1]
    return data


def base64_to_bytes(data: str) -> bytes:
    """Decode a (possibly data-URI-prefixed) Base64 string to raw bytes."""
    return base64.b64decode(strip_data_uri(data))


def bytes_to_base64(raw: bytes) -> str:
    """Encode raw bytes to a Base64 string."""
    return base64.b64encode(raw).decode("utf-8")
