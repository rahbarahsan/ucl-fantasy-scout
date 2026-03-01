"""Pipeline orchestrator — runs all agents in sequence."""

from typing import Any, Optional, Union

from app.agents.fixture_resolver.agent import resolve_fixtures
from app.agents.form_analyser.agent import analyse_form
from app.agents.matchday_validator.agent import validate_matchday
from app.agents.preview_researcher.agent import research_previews
from app.agents.squad_parser.agent import parse_squad
from app.agents.stats_collector.agent import collect_stats
from app.agents.transfer_suggester.agent import suggest_transfers
from app.agents.verdict_engine.agent import generate_verdicts
from app.config import settings
from app.providers.anthropic import AnthropicProvider
from app.providers.base import AIProvider
from app.providers.gemini import GeminiProvider
from app.schemas.analysis import (
    Alternative,
    AnalysisResponse,
    MatchdayClarification,
    PlayerResult,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _get_provider(
    provider_name: str,
    api_key: Optional[str] = None,
) -> AIProvider:
    """Instantiate the requested AI provider."""
    if provider_name == "anthropic":
        key = api_key or settings.anthropic_api_key
        if not key:
            raise ValueError("Anthropic API key is not configured.")
        return AnthropicProvider(api_key=key)
    if provider_name == "gemini":
        key = api_key or settings.gemini_api_key
        if not key:
            raise ValueError("Gemini API key is not configured.")
        return GeminiProvider(api_key=key)
    raise ValueError(f"Unknown provider: {provider_name}")


async def run_analysis(
    image_base64: str,
    provider_name: str = "anthropic",
    user_matchday: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Union[AnalysisResponse, MatchdayClarification]:
    """Execute the full agent pipeline and return a structured report.

    Returns a ``MatchdayClarification`` if the matchday cannot be determined.
    """
    provider = _get_provider(provider_name, api_key=api_key)

    # --- Agent 1: Squad Parser -------------------------------------------
    logger.info("pipeline_agent_1_squad_parser")
    squad_data = await parse_squad(provider, image_base64)
    players = squad_data.get("players", [])
    extracted_matchday = squad_data.get("matchday")

    if not players:
        logger.error("pipeline_no_players_extracted")
        raise ValueError(
            "Could not extract any players from the screenshot. "
            "Please try a clearer image."
        )

    # --- Agent 2: Matchday Validator -------------------------------------
    logger.info("pipeline_agent_2_matchday_validator")
    matchday_result = await validate_matchday(
        provider,
        extracted_matchday,
        user_matchday=user_matchday,
    )

    if not matchday_result.get("confirmed"):
        return MatchdayClarification(
            needs_clarification=True,
            message=matchday_result.get(
                "message",
                "Could not determine the matchday. Please specify it manually.",
            ),
        )

    matchday = matchday_result["matchday"]
    early_warning = matchday_result.get("early_warning", False)

    # --- Agent 3: Fixture Resolver ---------------------------------------
    logger.info("pipeline_agent_3_fixture_resolver")
    fixtures = await resolve_fixtures(provider, matchday, players)

    # --- Agent 4: Preview Researcher -------------------------------------
    logger.info("pipeline_agent_4_preview_researcher")
    previews = await research_previews(provider, fixtures)

    # --- Agent 5: Form Analyser ------------------------------------------
    logger.info("pipeline_agent_5_form_analyser")
    form_data = await analyse_form(provider, players, fixtures)

    # --- Agent 6: Stats Collector ----------------------------------------
    logger.info("pipeline_agent_6_stats_collector")
    stats = await collect_stats(provider, players)

    # --- Agent 7: Verdict Engine -----------------------------------------
    logger.info("pipeline_agent_7_verdict_engine")
    verdicts = await generate_verdicts(
        provider,
        players,
        previews,
        form_data,
        stats,
    )

    # --- Agent 8: Transfer Suggester -------------------------------------
    logger.info("pipeline_agent_8_transfer_suggester")
    suggestions = await suggest_transfers(provider, verdicts)

    # --- Assemble final response -----------------------------------------
    return _build_response(
        matchday=matchday,
        early_warning=early_warning,
        verdicts=verdicts,
        suggestions=suggestions,
    )


def _build_response(
    matchday: str,
    early_warning: bool,
    verdicts: list[dict[str, Any]],
    suggestions: dict[str, list[dict[str, Any]]],
) -> AnalysisResponse:
    """Convert raw agent output into a typed ``AnalysisResponse``."""
    player_results: list[PlayerResult] = []

    for verdict in verdicts:
        name = verdict.get("name", "Unknown")
        alts_raw = suggestions.get(name, [])
        alternatives = [
            Alternative(
                name=a.get("name", ""),
                team=a.get("team", ""),
                position=a.get("position", ""),
                price=a.get("price", ""),
                reason=a.get("reason", ""),
            )
            for a in alts_raw
        ]
        player_results.append(
            PlayerResult(
                name=name,
                position=verdict.get("position", "MID"),
                team=verdict.get("team", ""),
                status=verdict.get("status", "RISK"),
                reason=verdict.get("reason", ""),
                confidence=verdict.get("confidence", "MEDIUM"),
                price=verdict.get("price", ""),
                is_substitute=verdict.get("is_substitute", False),
                alternatives=alternatives,
            )
        )

    return AnalysisResponse(
        matchday=matchday,
        matchday_confirmed=True,
        analysis_day="BOTH",
        early_warning=early_warning,
        players=player_results,
    )
