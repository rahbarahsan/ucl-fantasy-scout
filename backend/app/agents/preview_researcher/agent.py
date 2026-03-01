"""Preview Researcher agent — searches for match previews and expected lineups."""

import json
from typing import Any, Union

from app.agents.preview_researcher.prompts import SYSTEM_PROMPT
from app.agents.preview_researcher.sources import PREVIEW_KEYWORDS
from app.cache.cache_manager import cache_manager
from app.config import settings
from app.providers.base import AIProvider
from app.tools.web_search import web_search
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def research_previews(
    provider: AIProvider,
    fixtures: Union[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    """Search for match previews for each fixture.

    Args:
        provider: AI provider instance
        fixtures: Either a cache key (str) or fixtures list (list[dict])
    
    Uses web search when available, then passes results to the AI for synthesis.
    Returns: {"cache_key": "previews:...", "count": N}
    """
    # Handle both cache keys and direct data (for flexibility)
    if isinstance(fixtures, str):
        # Received cache key
        cache_key = fixtures
        fixtures_data = cache_manager.get(cache_key)
        logger.info("preview_researcher_start", fixtures_cache_key=cache_key)
    else:
        # Received direct data
        fixtures_data = fixtures
        logger.info("preview_researcher_start", fixture_count=len(fixtures_data))

    # Build search context from web results
    search_context = await _gather_search_context(fixtures_data)

    fixture_text = "\n".join(
        f"- {f.get('team', '?')} vs {f.get('opponent', '?')}" for f in fixtures_data
    )

    prompt = (
        f"Fixtures:\n{fixture_text}\n\n"
        f"Web search results:\n{search_context}\n\n"
        "Please provide match previews with expected lineups, injury news, "
        "and rotation hints for each fixture."
    )

    raw = await provider.complete(prompt, system_prompt=SYSTEM_PROMPT)
    previews = _parse_response(raw)
    
    # Cache the previews and return cache key
    cache_key = f"previews:agent4"
    cache_manager.set(cache_key, previews)
    
    logger.info("preview_researcher_done", 
                preview_count=len(previews),
                cache_key=cache_key)
    
    # Return cache key instead of full data
    return {
        "cache_key": cache_key,
        "count": len(previews)
    }


async def _gather_search_context(
    fixtures: list[dict[str, Any]],
) -> str:
    """Run web searches for each fixture and compile context."""
    lines: list[str] = []
    for fixture in fixtures:
        team = fixture.get("team", "")
        opponent = fixture.get("opponent", "")
        if not team or not opponent or opponent == "unknown":
            continue
        query = f"{team} vs {opponent} {PREVIEW_KEYWORDS[0]}"
        results = await web_search(
            query,
            num_results=3,
            recency_days=7,
            serpapi_key=settings.serpapi_key,
        )
        for result in results:
            lines.append(
                f"[{result.get('title', '')}] {result.get('snippet', '')} "
                f"({result.get('link', '')})"
            )
    return "\n".join(lines) if lines else "No web search results available."


def _parse_response(raw: str) -> list[dict[str, Any]]:
    """Parse the JSON previews response."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
        return data.get("previews", [])
    except json.JSONDecodeError:
        logger.error("preview_researcher_json_failed")
        return []
