"""Preview Researcher agent — searches for match previews and expected lineups."""

import json
from typing import Any

from app.agents.preview_researcher.prompts import SYSTEM_PROMPT
from app.agents.preview_researcher.sources import PREVIEW_KEYWORDS
from app.config import settings
from app.providers.base import AIProvider
from app.tools.web_search import web_search
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def research_previews(
    provider: AIProvider,
    fixtures: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Search for match previews for each fixture.

    Uses web search when available, then passes results to the AI for synthesis.
    """
    logger.info("preview_researcher_start", fixture_count=len(fixtures))

    # Build search context from web results
    search_context = await _gather_search_context(fixtures)

    fixture_text = "\n".join(
        f"- {f.get('team', '?')} vs {f.get('opponent', '?')}" for f in fixtures
    )

    prompt = (
        f"Fixtures:\n{fixture_text}\n\n"
        f"Web search results:\n{search_context}\n\n"
        "Please provide match previews with expected lineups, injury news, "
        "and rotation hints for each fixture."
    )

    raw = await provider.complete(prompt, system_prompt=SYSTEM_PROMPT)
    previews = _parse_response(raw)
    logger.info("preview_researcher_done", preview_count=len(previews))
    return previews


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
