"""Fixture Resolver agent — maps squads to UCL fixtures."""

import json
from typing import Any

from app.agents.fixture_resolver.prompts import SYSTEM_PROMPT
from app.cache.cache_manager import cache_manager
from app.providers.base import AIProvider
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def resolve_fixtures(
    provider: AIProvider,
    matchday: str,
    players: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return a cache key for fixture list for each unique club in *players*.

    Returns: {"cache_key": "fixtures:...", "count": N}
    """
    teams = sorted({p["team"] for p in players if p.get("team")})
    logger.info("fixture_resolver_start", matchday=matchday, team_count=len(teams))

    prompt = (
        f"Matchday: {matchday}\n"
        f"Teams: {', '.join(teams)}\n\n"
        "Please provide the UCL fixture for each team on this matchday."
    )

    raw = await provider.complete(prompt, system_prompt=SYSTEM_PROMPT)
    fixtures = _parse_response(raw)

    # Cache the fixtures and return cache key
    cache_key = f"fixtures:agent3:{matchday}"
    cache_manager.set(cache_key, fixtures)

    logger.info(
        "fixture_resolver_done", fixture_count=len(fixtures), cache_key=cache_key
    )

    # Return cache key instead of full data
    return {"cache_key": cache_key, "count": len(fixtures)}


def _parse_response(raw: str) -> list[dict[str, Any]]:
    """Parse the JSON fixtures response."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
        return data.get("fixtures", [])
    except json.JSONDecodeError:
        logger.error("fixture_resolver_json_failed")
        return []
