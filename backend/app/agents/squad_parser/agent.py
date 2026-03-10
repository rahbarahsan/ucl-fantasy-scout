"""Squad Parser agent — uses vision AI to extract squad data from a screenshot."""

from typing import Any

from app.agents.squad_parser.prompts import SYSTEM_PROMPT, USER_PROMPT
from app.providers.base import AIProvider
from app.utils.json_parser import parse_json_response
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
    data = parse_json_response(raw, fallback={"matchday": None, "players": []})
    return {
        "matchday": data.get("matchday"),
        "players": data.get("players", []),
    }
