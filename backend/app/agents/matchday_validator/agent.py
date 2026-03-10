"""Matchday Validator agent — confirms matchday or requests clarification."""

from typing import Any, Optional

from app.agents.matchday_validator.prompts import SYSTEM_PROMPT
from app.providers.base import AIProvider
from app.utils.json_parser import parse_json_response
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def validate_matchday(
    provider: AIProvider,
    extracted_matchday: Optional[str],
    user_matchday: Optional[str] = None,
) -> dict[str, Any]:
    """Return a validated matchday dict.

    If *user_matchday* is provided it takes priority over the extracted value.
    """
    logger.info(
        "matchday_validator_start",
        extracted=extracted_matchday,
        user_provided=user_matchday,
    )

    # User explicitly provided a matchday — trust it
    if user_matchday:
        return {
            "matchday": user_matchday,
            "confirmed": True,
            "early_warning": False,
            "message": None,
        }

    # Nothing extracted — ask for clarification
    if not extracted_matchday:
        return {
            "matchday": None,
            "confirmed": False,
            "early_warning": False,
            "message": (
                "We could not confirm the matchday from your screenshot. "
                "Could you tell us which matchday this is?"
            ),
        }

    # Ask the model to validate the extracted value
    prompt = (
        f"The squad screenshot appears to show: {extracted_matchday}. "
        "Please validate this matchday."
    )
    raw = await provider.complete(prompt, system_prompt=SYSTEM_PROMPT)
    return _parse_response(raw, fallback_matchday=extracted_matchday)


def _parse_response(raw: str, fallback_matchday: Optional[str]) -> dict[str, Any]:
    """Parse the JSON validation response from the model."""
    data = parse_json_response(
        raw,
        fallback={
            "matchday": fallback_matchday,
            "confirmed": bool(fallback_matchday),
            "early_warning": False,
            "message": None,
        },
    )
    return {
        "matchday": data.get("matchday", fallback_matchday),
        "confirmed": data.get("confirmed", False),
        "early_warning": data.get("early_warning", False),
        "message": data.get("message"),
    }
