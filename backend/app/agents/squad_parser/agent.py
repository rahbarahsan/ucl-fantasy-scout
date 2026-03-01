"""Squad Parser agent — uses vision AI to extract squad data from a screenshot."""

import json
from typing import Any, Optional

from app.agents.squad_parser.prompts import SYSTEM_PROMPT, USER_PROMPT
from app.providers.base import AIProvider
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def parse_squad(
    provider: AIProvider,
    image_base64: str,
) -> dict[str, Any]:
    """Extract players and matchday from a squad screenshot.

    Returns a dict with keys ``matchday`` (str | None) and ``players`` (list).
    """
    logger.info("squad_parser_start")

    raw = await provider.analyse_image(
        image_base64,
        USER_PROMPT,
        system_prompt=SYSTEM_PROMPT,
    )

    parsed = _parse_response(raw)
    player_count = len(parsed.get("players", []))
    logger.info("squad_parser_done", player_count=player_count)
    return parsed


def _parse_response(raw: str) -> dict[str, Any]:
    """Attempt to parse the model's JSON response."""
    # Strip markdown code fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.error("squad_parser_json_failed", raw_length=len(raw))
        return {"matchday": None, "players": []}

    return {
        "matchday": data.get("matchday"),
        "players": data.get("players", []),
    }
