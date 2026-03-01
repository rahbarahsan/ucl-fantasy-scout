"""Tests for the Squad Parser agent."""

from unittest.mock import AsyncMock

import pytest

from app.agents.squad_parser.agent import parse_squad


@pytest.fixture
def mock_provider() -> AsyncMock:
    """Return a mock AI provider."""
    return AsyncMock()


class TestParseSquad:
    """Tests for parse_squad."""

    @pytest.mark.asyncio
    async def test_successful_parse(self, mock_provider: AsyncMock) -> None:
        """Valid JSON response should be parsed correctly."""
        mock_provider.analyse_image.return_value = (
            '{"matchday": "Matchday 5", "players": ['
            '{"name": "Haaland", "position": "FWD", "team": "Man City", '
            '"price": "11.5", "is_substitute": false}'
            "]}"
        )
        result = await parse_squad(mock_provider, "base64data")
        assert result["matchday"] == "Matchday 5"
        assert len(result["players"]) == 1
        assert result["players"][0]["name"] == "Haaland"

    @pytest.mark.asyncio
    async def test_invalid_json_returns_empty(
        self,
        mock_provider: AsyncMock,
    ) -> None:
        """Invalid JSON should return an empty structure."""
        mock_provider.analyse_image.return_value = "This is not JSON at all."
        result = await parse_squad(mock_provider, "base64data")
        assert result["matchday"] is None
        assert result["players"] == []

    @pytest.mark.asyncio
    async def test_markdown_fenced_json(self, mock_provider: AsyncMock) -> None:
        """JSON wrapped in markdown code fences should be parsed."""
        mock_provider.analyse_image.return_value = (
            '```json\n{"matchday": "Matchday 3", "players": []}\n```'
        )
        result = await parse_squad(mock_provider, "base64data")
        assert result["matchday"] == "Matchday 3"
