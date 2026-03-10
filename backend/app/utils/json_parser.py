"""Utility for parsing JSON responses from AI models."""

import json
from typing import Any, Dict

from app.utils.logger import get_logger

logger = get_logger(__name__)


def parse_json_response(raw: str, fallback: Any = None) -> Dict[str, Any]:
    """Parse JSON from AI response, handling markdown code fences.

    Args:
        raw: Raw string response from AI model
        fallback: Value to return if parsing fails (default: empty dict)

    Returns:
        Parsed JSON as dictionary, or fallback value if parsing fails
    """
    if fallback is None:
        fallback = {}

    cleaned = raw.strip()

    # Remove markdown code fences if present
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
        return data if isinstance(data, dict) else fallback
    except json.JSONDecodeError as exc:
        logger.error("json_parse_failed", error=str(exc), raw_preview=raw[:100])
        return fallback
