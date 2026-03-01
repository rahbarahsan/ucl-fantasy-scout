"""Tests for the Verdict Engine agent."""

from unittest.mock import AsyncMock

import pytest

from app.agents.verdict_engine.agent import generate_verdicts


@pytest.fixture
def mock_provider() -> AsyncMock:
    """Return a mock AI provider."""
    return AsyncMock()


@pytest.fixture
def sample_players() -> list[dict]:
    """Return a small sample player list."""
    return [
        {
            "name": "Haaland",
            "position": "FWD",
            "team": "Man City",
            "price": "11.5",
            "is_substitute": False,
        },
    ]


class TestGenerateVerdicts:
    """Tests for generate_verdicts."""

    @pytest.mark.asyncio
    async def test_successful_verdicts(
        self,
        mock_provider: AsyncMock,
        sample_players: list[dict],
    ) -> None:
        """Valid response should parse into verdicts."""
        mock_provider.complete.return_value = (
            '{"verdicts": [{"name": "Haaland", "team": "Man City", '
            '"position": "FWD", "status": "START", "confidence": "HIGH", '
            '"reason": "Nailed starter.", "price": "11.5", '
            '"is_substitute": false}]}'
        )
        result = await generate_verdicts(
            mock_provider,
            sample_players,
            previews=[],
            form_data=[],
            stats=[],
        )
        assert len(result) == 1
        assert result[0]["status"] == "START"

    @pytest.mark.asyncio
    async def test_invalid_json_returns_empty(
        self,
        mock_provider: AsyncMock,
        sample_players: list[dict],
    ) -> None:
        """Invalid JSON should return empty list."""
        mock_provider.complete.return_value = "not json"
        result = await generate_verdicts(
            mock_provider,
            sample_players,
            previews=[],
            form_data=[],
            stats=[],
        )
        assert result == []
