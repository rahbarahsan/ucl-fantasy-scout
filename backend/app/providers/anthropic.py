"""Anthropic Claude provider implementation."""

from typing import Any, Optional

import anthropic

from app.providers.base import AIProvider
from app.utils.logger import get_logger

logger = get_logger(__name__)

_DEFAULT_MODEL = "claude-sonnet-4-20250514"
_MAX_TOKENS = 4096


class AnthropicProvider(AIProvider):
    """Wrapper around the Anthropic Python SDK."""

    def __init__(self, api_key: str, model: str = _DEFAULT_MODEL) -> None:
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    # -- public interface -------------------------------------------------

    async def analyse_image(
        self,
        image_base64: str,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Send an image with a prompt to Claude's vision endpoint."""
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_base64,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        kwargs: dict[str, Any] = {
            "model": self._model,
            "max_tokens": _MAX_TOKENS,
            "messages": messages,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = await self._client.messages.create(**kwargs)
        return self._extract_text(response)

    async def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        system_prompt: Optional[str] = None,
        tools: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """Multi-turn conversation, optionally with tool definitions."""
        kwargs: dict[str, Any] = {
            "model": self._model,
            "max_tokens": _MAX_TOKENS,
            "messages": messages,
        }
        if system_prompt:
            kwargs["system"] = system_prompt
        if tools:
            kwargs["tools"] = tools

        response = await self._client.messages.create(**kwargs)
        return self._response_to_dict(response)

    async def complete(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Simple single-turn completion."""
        messages = [{"role": "user", "content": prompt}]
        kwargs: dict[str, Any] = {
            "model": self._model,
            "max_tokens": _MAX_TOKENS,
            "messages": messages,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = await self._client.messages.create(**kwargs)
        return self._extract_text(response)

    # -- helpers ----------------------------------------------------------

    @staticmethod
    def _extract_text(response: Any) -> str:
        """Pull plain text from the first text content block."""
        for block in response.content:
            if hasattr(block, "text"):
                return block.text
        return ""

    @staticmethod
    def _response_to_dict(response: Any) -> dict[str, Any]:
        """Convert an Anthropic response to a serialisable dict."""
        content_blocks = []
        for block in response.content:
            if hasattr(block, "text"):
                content_blocks.append({"type": "text", "text": block.text})
            elif hasattr(block, "type") and block.type == "tool_use":
                content_blocks.append(
                    {
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    }
                )
        return {
            "role": "assistant",
            "content": content_blocks,
            "stop_reason": response.stop_reason,
        }
