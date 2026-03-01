"""Integration tests for the full agent pipeline."""

from unittest.mock import AsyncMock, patch

import pytest

from app.agents.pipeline import run_analysis
from app.schemas.analysis import AnalysisResponse, MatchdayClarification


@pytest.fixture
def mock_provider() -> AsyncMock:
    """Return a mock provider that responds with valid JSON."""
    provider = AsyncMock()

    # Agent 1 — Squad Parser
    provider.analyse_image.return_value = (
        '{"matchday": "Matchday 5", "players": ['
        '{"name": "Haaland", "position": "FWD", "team": "Man City", '
        '"price": "11.5", "is_substitute": false}]}'
    )

    # Default complete responses for each subsequent agent
    provider.complete.side_effect = [
        # Agent 2 — Matchday Validator
        '{"matchday": "Matchday 5", "confirmed": true, '
        '"early_warning": false, "message": null}',
        # Agent 3 — Fixture Resolver
        '{"fixtures": [{"team": "Man City", "opponent": "Inter Milan", '
        '"home_away": "HOME", "match_date": "2026-02-28", '
        '"match_day_number": 1}]}',
        # Agent 4 — Preview Researcher
        '{"previews": [{"team": "Man City", "opponent": "Inter Milan", '
        '"expected_lineup": ["Haaland"], "injury_news": "None", '
        '"rotation_hints": "None", "key_quotes": "", "sources": []}]}',
        # Agent 5 — Form Analyser
        '{"form_data": [{"name": "Haaland", "team": "Man City", '
        '"recent_minutes": [90, 70, 90], "last_match_minutes": 90, '
        '"rotation_risk": "LOW", "form_notes": "Consistent starter"}]}',
        # Agent 6 — Stats Collector
        '{"stats": [{"name": "Haaland", "team": "Man City", '
        '"ucl_goals": 5, "ucl_assists": 2, "ucl_clean_sheets": null, '
        '"ucl_minutes": 450, "ucl_appearances": 5, '
        '"league_goals": 15, "league_assists": 3, "league_minutes": 1800, '
        '"form_rating": "GOOD", "notes": "Top scorer"}]}',
        # Agent 7 — Verdict Engine
        '{"verdicts": [{"name": "Haaland", "team": "Man City", '
        '"position": "FWD", "status": "START", "confidence": "HIGH", '
        '"reason": "Nailed starter with excellent form.", '
        '"price": "11.5", "is_substitute": false}]}',
        # Agent 8 — Transfer Suggester (no at-risk players)
        '{"suggestions": []}',
    ]
    return provider


class TestPipelineIntegration:
    """End-to-end pipeline tests with mocked providers."""

    @pytest.mark.asyncio
    async def test_full_pipeline_returns_analysis(
        self,
        mock_provider: AsyncMock,
    ) -> None:
        """A valid image should produce an AnalysisResponse."""
        with patch(
            "app.agents.pipeline._get_provider",
            return_value=mock_provider,
        ):
            result = await run_analysis(
                image_base64="fake-base64",
                provider_name="anthropic",
                user_matchday="Matchday 5",
                api_key="test-key",
            )
        assert isinstance(result, AnalysisResponse)
        assert result.matchday == "Matchday 5"
        assert len(result.players) == 1
        assert result.players[0].status == "START"

    @pytest.mark.asyncio
    async def test_missing_matchday_returns_clarification(self) -> None:
        """When matchday is unclear, a clarification should be returned."""
        provider = AsyncMock()
        provider.analyse_image.return_value = (
            '{"matchday": null, "players": ['
            '{"name": "Salah", "position": "FWD", "team": "Liverpool", '
            '"price": "10.0", "is_substitute": false}]}'
        )

        with patch(
            "app.agents.pipeline._get_provider",
            return_value=provider,
        ):
            result = await run_analysis(
                image_base64="fake-base64",
                provider_name="anthropic",
                api_key="test-key",
            )
        assert isinstance(result, MatchdayClarification)
        assert result.needs_clarification is True
