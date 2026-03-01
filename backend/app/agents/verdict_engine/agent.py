"""Verdict Engine agent — produces START / RISK / BENCH for each player."""

import json
from typing import Any

from app.agents.verdict_engine.prompts import SYSTEM_PROMPT
from app.providers.base import AIProvider
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def generate_verdicts(
    provider: AIProvider,
    players: list[dict[str, Any]],
    previews: list[dict[str, Any]],
    form_data: list[dict[str, Any]],
    stats: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Synthesise all research into per-player verdicts."""
    logger.info("verdict_engine_start", player_count=len(players))

    prompt = _build_prompt(players, previews, form_data, stats)
    raw = await provider.complete(prompt, system_prompt=SYSTEM_PROMPT)
    verdicts = _parse_response(raw)
    logger.info("verdict_engine_done", verdict_count=len(verdicts))
    return verdicts


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
