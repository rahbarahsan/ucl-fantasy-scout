"""Form Analyser agent — assesses recent form and rotation risk."""

import json
from typing import Any

from app.agents.form_analyser.prompts import SYSTEM_PROMPT
from app.providers.base import AIProvider
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def analyse_form(
    provider: AIProvider,
    players: list[dict[str, Any]],
    fixtures: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return form data and rotation risk for each player."""
    logger.info("form_analyser_start", player_count=len(players))

    player_text = "\n".join(
        f"- {p.get('name', '?')} ({p.get('team', '?')}, {p.get('position', '?')})"
        for p in players
    )

    fixture_text = "\n".join(
        f"- {f.get('team', '?')} vs {f.get('opponent', '?')}" for f in fixtures
    )

    prompt = (
        f"Players:\n{player_text}\n\n"
        f"Upcoming UCL fixtures:\n{fixture_text}\n\n"
        "Analyse each player's recent form, minutes played in their last "
        "few matches, and assess their rotation risk for the upcoming UCL fixture."
    )

    raw = await provider.complete(prompt, system_prompt=SYSTEM_PROMPT)
    form_data = _parse_response(raw)
    logger.info("form_analyser_done", count=len(form_data))
    return form_data


def _parse_response(raw: str) -> list[dict[str, Any]]:
    """Parse JSON form data from model response."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
        return data.get("form_data", [])
    except json.JSONDecodeError:
        logger.error("form_analyser_json_failed")
        return []
