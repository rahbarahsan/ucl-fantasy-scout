"""Stats Collector agent — gathers UCL and league statistics."""

import json
from typing import Any

from app.agents.stats_collector.prompts import SYSTEM_PROMPT
from app.cache.cache_manager import cache_manager
from app.providers.base import AIProvider
from app.utils.cache_keys import build_cache_key
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def collect_stats(
    provider: AIProvider,
    players: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return season statistics for each player."""
    logger.info("stats_collector_start", player_count=len(players))

    player_text = "\n".join(
        f"- {p.get('name', '?')} ({p.get('team', '?')}, {p.get('position', '?')})"
        for p in players
    )

    prompt = (
        f"Players:\n{player_text}\n\n"
        "Provide UCL and domestic league stats for each player this season."
    )

    raw = await provider.complete(prompt, system_prompt=SYSTEM_PROMPT)
    stats = _parse_response(raw)

    # Cache the stats and return cache key
    cache_key = build_cache_key("stats:agent6", str(len(players)))
    cache_manager.set(cache_key, stats)

    logger.info("stats_collector_done", count=len(stats), cache_key=cache_key)
    return {"cache_key": cache_key, "count": len(stats)}


def _parse_response(raw: str) -> list[dict[str, Any]]:
    """Parse the JSON stats response."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
        return data.get("stats", [])
    except json.JSONDecodeError:
        logger.error("stats_collector_json_failed")
        return []
