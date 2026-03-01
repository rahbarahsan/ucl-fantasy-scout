"""Transfer Suggester agent — recommends replacements for RISK/BENCH players."""

import json
from typing import Any

from app.agents.transfer_suggester.prompts import SYSTEM_PROMPT
from app.providers.base import AIProvider
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def suggest_transfers(
    provider: AIProvider,
    verdicts: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Return transfer suggestions keyed by player name.

    Only processes players with status RISK or BENCH.
    """
    at_risk = [v for v in verdicts if v.get("status") in ("RISK", "BENCH")]
    if not at_risk:
        logger.info("transfer_suggester_skipped", reason="no_risk_or_bench_players")
        return {}

    logger.info("transfer_suggester_start", at_risk_count=len(at_risk))

    player_text = "\n".join(
        f"- {v.get('name')} | {v.get('position')} | {v.get('team')} | "
        f"Price: {v.get('price', '?')} | Status: {v.get('status')}"
        for v in at_risk
    )

    prompt = (
        f"Players needing replacements:\n{player_text}\n\n"
        "Suggest 1-2 alternative transfers for each player."
    )

    raw = await provider.complete(prompt, system_prompt=SYSTEM_PROMPT)
    return _parse_response(raw)


def _parse_response(raw: str) -> dict[str, list[dict[str, Any]]]:
    """Parse transfer suggestions, keyed by the original player name."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.error("transfer_suggester_json_failed")
        return {}

    result: dict[str, list[dict[str, Any]]] = {}
    for entry in data.get("suggestions", []):
        player_name = entry.get("for_player", "")
        result[player_name] = entry.get("alternatives", [])
    return result
