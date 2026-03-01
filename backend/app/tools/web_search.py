"""Web search abstraction — delegates to provider tool-use or SerpAPI."""

from typing import Any, Optional

import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)

_SERP_API_URL = "https://serpapi.com/search"
_DEFAULT_NUM_RESULTS = 5
_TIMEOUT = 15


async def web_search(
    query: str,
    *,
    num_results: int = _DEFAULT_NUM_RESULTS,
    recency_days: int = 7,
    serpapi_key: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Search the web and return a list of result dicts.

    Each result contains ``title``, ``link``, and ``snippet`` keys.
    Falls back to an empty list on failure so agents can degrade gracefully.
    """
    if serpapi_key:
        return await _serpapi_search(
            query,
            serpapi_key=serpapi_key,
            num_results=num_results,
            recency_days=recency_days,
        )

    # When no SerpAPI key is available, return an empty list.
    # Agents will rely on provider-native tool use instead.
    logger.info("no_search_key_available", query=query)
    return []


async def _serpapi_search(
    query: str,
    *,
    serpapi_key: str,
    num_results: int,
    recency_days: int,
) -> list[dict[str, Any]]:
    """Execute a SerpAPI search and normalise the results."""
    params = {
        "q": query,
        "api_key": serpapi_key,
        "num": num_results,
        "tbs": f"qdr:d{recency_days}",
        "engine": "google",
    }
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(_SERP_API_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as exc:
        logger.error("serpapi_request_failed", error=str(exc))
        return []

    results: list[dict[str, Any]] = []
    for item in data.get("organic_results", [])[:num_results]:
        results.append(
            {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
            }
        )
    return results
