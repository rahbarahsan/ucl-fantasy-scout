"""Fixture Resolver agent — maps squads to UCL fixtures."""

from typing import Any

from app.agents.fixture_resolver.prompts import SYSTEM_PROMPT
from app.cache.cache_manager import cache_manager
from app.config import settings
from app.providers.base import AIProvider
from app.tools.web_search import web_search
from app.utils.cache_keys import build_cache_key
from app.utils.json_parser import parse_json_response
from app.utils.logger import get_logger
from app.utils.matchday_normalizer import (
    get_search_friendly_matchday,
    normalize_matchday,
)

logger = get_logger(__name__)


# pylint: disable=too-many-locals
async def resolve_fixtures(
    provider: AIProvider,
    matchday: str,
    players: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return a cache key for fixture list for each unique club in *players*.

    Returns: {"cache_key": "fixtures:...", "count": N}
    """
    # Smart normalization for various input formats (R16, round of 16, etc.)
    original_matchday = matchday
    matchday = normalize_matchday(matchday)

    logger.info(
        "fixture_resolver_matchday_normalized",
        original=original_matchday,
        normalized=matchday,
    )

    teams = sorted({p["team"] for p in players if p.get("team")})
    logger.info("fixture_resolver_start", matchday=matchday, team_count=len(teams))

    # Convert to search-friendly format (e.g., "1st leg" → "first leg")
    search_matchday = get_search_friendly_matchday(matchday)

    # Search for current UCL fixtures
    search_query = f"UEFA Champions League {search_matchday} fixtures schedule 2026"
    search_results = await web_search(
        search_query,
        num_results=5,
        recency_days=14,
        serpapi_key=settings.serpapi_key,
    )

    search_context = "\n".join(
        f"[{r.get('title', '')}] {r.get('snippet', '')} ({r.get('link', '')})"
        for r in search_results
    )

    logger.info("fixture_resolver_search_complete", result_count=len(search_results))

    # If search returns no results, try fallback queries
    if not search_results:
        logger.warning("fixture_resolver_no_results", original_query=search_query)

        # Try simpler query without year and schedule
        fallback_query = f"UEFA Champions League {search_matchday} fixtures"
        logger.info("fixture_resolver_fallback_search", query=fallback_query)

        search_results = await web_search(
            fallback_query,
            num_results=5,
            recency_days=30,  # Expand recency window
            serpapi_key=settings.serpapi_key,
        )

        if not search_results:
            # Try even broader - just the stage name
            stage_only = search_matchday.split("-")[0].strip()  # e.g., "Round of 16"
            fallback_query2 = f"Champions League {stage_only} 2026"
            logger.info("fixture_resolver_fallback_search_2", query=fallback_query2)

            search_results = await web_search(
                fallback_query2,
                num_results=5,
                recency_days=30,
                serpapi_key=settings.serpapi_key,
            )

    # Build search context
    search_context = "\n".join(
        f"[{r.get('title', '')}] {r.get('snippet', '')} ({r.get('link', '')})"
        for r in search_results
    )

    # If still no results after fallbacks, return error
    if not search_results:
        logger.error(
            "fixture_resolver_all_searches_failed",
            message="All web search attempts returned no results.",
        )
        cache_key = build_cache_key("fixtures:agent3", matchday)
        cache_manager.set(cache_key, [])
        return {
            "cache_key": cache_key,
            "count": 0,
            "error": (
                f"Could not find fixtures for {matchday}. "
                "Please verify the matchday name or try again later."
            ),
        }

    logger.info(
        "fixture_resolver_using_search_results", result_count=len(search_results)
    )

    prompt = (
        f"Matchday: {matchday}\n"
        f"Teams: {', '.join(teams)}\n\n"
        f"Web search results for current UCL fixtures:\n{search_context}\n\n"
        "Based on the search results above, provide the UCL fixture "
        "for each team on this matchday."
    )

    raw = await provider.complete(prompt, system_prompt=SYSTEM_PROMPT)
    fixtures = _parse_response(raw)

    # Cache the fixtures and return cache key
    cache_key = build_cache_key("fixtures:agent3", matchday)
    cache_manager.set(cache_key, fixtures)

    logger.info(
        "fixture_resolver_done", fixture_count=len(fixtures), cache_key=cache_key
    )

    # Return cache key instead of full data
    return {"cache_key": cache_key, "count": len(fixtures)}


def _parse_response(raw: str) -> list[dict[str, Any]]:
    """Parse the JSON fixtures response."""
    data = parse_json_response(raw, fallback={})
    return data.get("fixtures", [])
