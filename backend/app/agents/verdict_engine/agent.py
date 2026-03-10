"""Verdict Engine agent — produces START / RISK / BENCH for each player."""

import json
from typing import Any, Union

from app.agents.verdict_engine.prompts import SYSTEM_PROMPT
from app.cache.cache_manager import cache_manager
from app.providers.base import AIProvider
from app.utils.cache_keys import build_cache_key
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def generate_verdicts(
    provider: AIProvider,
    players: list[dict[str, Any]],
    previews_input: Union[str, list[dict[str, Any]]],
    form_data_input: Union[str, dict[str, Any]],
    stats_input: Union[str, dict[str, Any]],
) -> dict[str, Any]:
    """Synthesise all research into per-player verdicts."""
    logger.info("verdict_engine_start", player_count=len(players))

    # Retrieve data from cache if cache keys provided
    if isinstance(previews_input, str):
        previews = cache_manager.get(previews_input) or []
    else:
        previews = previews_input

    if isinstance(form_data_input, str):
        form_data = cache_manager.get(form_data_input) or []
    else:
        form_data = form_data_input if isinstance(form_data_input, list) else []

    if isinstance(stats_input, str):
        stats = cache_manager.get(stats_input) or []
    else:
        stats = stats_input if isinstance(stats_input, list) else []

    prompt = _build_prompt(players, previews, form_data, stats)
    raw = await provider.complete(prompt, system_prompt=SYSTEM_PROMPT)
    verdicts = _parse_response(raw)

    # Cache the verdicts and return cache key
    cache_key = build_cache_key("verdicts:agent7", str(len(players)))
    cache_manager.set(cache_key, verdicts)

    logger.info("verdict_engine_done", verdict_count=len(verdicts), cache_key=cache_key)
    return {"cache_key": cache_key, "count": len(verdicts)}


def _build_prompt(
    players: list[dict[str, Any]],
    previews: list[dict[str, Any]],
    form_data: list[dict[str, Any]],
    stats: list[dict[str, Any]],
) -> str:
    """Assemble the full context prompt for the verdict engine."""
    sections: list[str] = []

    sections.append("=== PLAYERS ===")
    for p in players:
        sections.append(
            f"- {p.get('name')} | {p.get('position')} | {p.get('team')} | "
            f"Price: {p.get('price', '?')} | Sub: {p.get('is_substitute', False)}"
        )

    sections.append("\n=== MATCH PREVIEWS ===")
    for pr in previews:
        sections.append(
            f"- {pr.get('team')} vs {pr.get('opponent')}: "
            f"Lineup: {pr.get('expected_lineup', 'N/A')} | "
            f"Injuries: {pr.get('injury_news', 'N/A')} | "
            f"Rotation: {pr.get('rotation_hints', 'N/A')}"
        )

    sections.append("\n=== FORM DATA ===")
    for fd in form_data:
        sections.append(
            f"- {fd.get('name')} ({fd.get('team')}): "
            f"Last match: {fd.get('last_match_minutes', '?')} min | "
            f"Rotation risk: {fd.get('rotation_risk', '?')} | "
            f"{fd.get('form_notes', '')}"
        )

    sections.append("\n=== STATS ===")
    for st in stats:
        sections.append(
            f"- {st.get('name')} ({st.get('team')}): "
            f"UCL: {st.get('ucl_goals', 0)}G {st.get('ucl_assists', 0)}A | "
            f"League: {st.get('league_goals', 0)}G {st.get('league_assists', 0)}A | "
            f"Form: {st.get('form_rating', '?')}"
        )

    sections.append(
        "\nBased on all the above data, provide a START / RISK / BENCH "
        "verdict for every player with reasoning."
    )

    return "\n".join(sections)


def _parse_response(raw: str) -> list[dict[str, Any]]:
    """Parse the JSON verdicts response."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
        return data.get("verdicts", [])
    except json.JSONDecodeError:
        logger.error("verdict_engine_json_failed")
        return []
