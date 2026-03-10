"""Transfer Suggester agent — recommends replacements for RISK/BENCH players."""

from typing import Any, Union

from app.agents.transfer_suggester.prompts import SYSTEM_PROMPT
from app.cache.cache_manager import cache_manager
from app.providers.base import AIProvider
from app.utils.cache_keys import build_cache_key
from app.utils.json_parser import parse_json_response
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def suggest_transfers(
    provider: AIProvider,
    verdicts_input: Union[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    """Return transfer suggestions keyed by player name.

    Only processes players with status RISK or BENCH.
    """
    # Retrieve verdicts from cache if cache key provided
    if isinstance(verdicts_input, str):
        verdicts = cache_manager.get(verdicts_input) or []
    else:
        verdicts = verdicts_input

    at_risk = [v for v in verdicts if v.get("status") in ("RISK", "BENCH")]
    if not at_risk:
        cache_key = build_cache_key("transfers:agent8", "none")
        cache_manager.set(cache_key, {})
        logger.info(
            "transfer_suggester_skipped",
            reason="no_risk_or_bench_players",
            cache_key=cache_key,
        )
        return {"cache_key": cache_key, "count": 0}

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
    suggestions = _parse_response(raw)

    # Cache the suggestions and return cache key
    cache_key = build_cache_key("transfers:agent8", str(len(at_risk)))
    cache_manager.set(cache_key, suggestions)

    logger.info("transfer_suggester_done", count=len(suggestions), cache_key=cache_key)
    return {"cache_key": cache_key, "count": len(suggestions)}


def _parse_response(raw: str) -> dict[str, list[dict[str, Any]]]:
    """Parse transfer suggestions, keyed by the original player name."""
    data = parse_json_response(raw, fallback={})

    result: dict[str, list[dict[str, Any]]] = {}
    for entry in data.get("suggestions", []):
        player_name = entry.get("for_player", "")
        result[player_name] = entry.get("alternatives", [])
    return result
