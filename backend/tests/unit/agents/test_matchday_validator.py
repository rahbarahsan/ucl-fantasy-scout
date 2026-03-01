"""Tests for the Matchday Validator agent."""

from unittest.mock import AsyncMock

import pytest

from app.agents.matchday_validator.agent import validate_matchday


@pytest.fixture
def mock_provider() -> AsyncMock:
    """Return a mock AI provider."""
    return AsyncMock()


class TestValidateMatchday:
    """Tests for validate_matchday."""

    @pytest.mark.asyncio
    async def test_user_provided_matchday(
        self,
        mock_provider: AsyncMock,
    ) -> None:
        """User-provided matchday should be trusted directly."""
        result = await validate_matchday(
            mock_provider,
            extracted_matchday=None,
            user_matchday="Matchday 5",
        )
        assert result["matchday"] == "Matchday 5"
        assert result["confirmed"] is True
        # Provider should not be called when user provides matchday
        mock_provider.complete.assert_not_called()

    @pytest.mark.asyncio
    async def test_no_matchday_returns_clarification(
        self,
        mock_provider: AsyncMock,
    ) -> None:
        """Missing matchday should request clarification."""
        result = await validate_matchday(
            mock_provider,
            extracted_matchday=None,
        )
        assert result["confirmed"] is False
        assert "could not confirm" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_extracted_matchday_validated(
        self,
        mock_provider: AsyncMock,
    ) -> None:
        """Extracted matchday should be validated via the provider."""
        mock_provider.complete.return_value = (
            '{"matchday": "Matchday 4", "confirmed": true, '
            '"early_warning": false, "message": null}'
        )
        result = await validate_matchday(
            mock_provider,
            extracted_matchday="Matchday 4",
        )
        assert result["confirmed"] is True
        assert result["matchday"] == "Matchday 4"
