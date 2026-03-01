"""Application configuration loaded from environment variables."""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings, loaded from .env or environment."""

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # AI providers
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # Tools
    serpapi_key: Optional[str] = None

    # Encryption
    encryption_secret: str = "change-me-to-a-random-32-char-secret"

    # App
    environment: str = "development"
    log_level: str = "INFO"

    @property
    def is_development(self) -> bool:
        """Return True when running in development mode."""
        return self.environment.lower() == "development"

    def has_anthropic_key(self) -> bool:
        """Check whether an Anthropic key is configured server-side."""
        return bool(self.anthropic_api_key)

    def has_gemini_key(self) -> bool:
        """Check whether a Gemini key is configured server-side."""
        return bool(self.gemini_api_key)


settings = Settings()
