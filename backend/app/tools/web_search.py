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

    # Console output for debugging
    print("\n🔍 SerpAPI SEARCH CALLED")
    print(f"   Query: {query}")
    print(f"   Results: {num_results}")
    print(f"   Recency: {recency_days} days")

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(_SERP_API_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

        # Log search results
        result_count = len(data.get("organic_results", []))
        logger.info(
            "serpapi_search_success",
            query=query,
            results_returned=result_count,
            search_time_ms=data.get("search_metadata", {}).get("total_time_taken", 0),
        )
        print(f"   ✅ Results Found: {result_count}")
        print()

    except httpx.HTTPError as exc:
        logger.error("serpapi_request_failed", query=query, error=str(exc))
        print(f"   ❌ Error: {str(exc)}\n")
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
