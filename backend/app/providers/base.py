"""Abstract base class for all AI providers."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class AIProvider(ABC):
    """Unified interface for vision + text + tool-use AI providers."""

    @abstractmethod
    async def analyse_image(
        self,
        image_base64: str,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Send an image (Base64) with a text prompt and return the model response."""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        system_prompt: Optional[str] = None,
        tools: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """Send a multi-turn conversation and return the assistant response.

        When *tools* are supplied the response may contain tool-use blocks
        that the caller must handle.
        """

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Simple single-turn text completion."""
