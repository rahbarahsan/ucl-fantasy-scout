"""Google Gemini provider implementation."""

from typing import Any, Optional

import google.generativeai as genai

from app.providers.base import AIProvider
from app.utils.image import base64_to_bytes
from app.utils.logger import get_logger
from app.utils.token_tracker import get_tracker

logger = get_logger(__name__)

_DEFAULT_MODEL = "gemini-2.0-flash"


class GeminiProvider(AIProvider):
    """Wrapper around the Google Generative AI SDK."""

    def __init__(self, api_key: str, model: str = _DEFAULT_MODEL) -> None:
        genai.configure(api_key=api_key)
        self._model_name = model

    # -- helpers ----------------------------------------------------------

    def _get_model(
        self,
        system_prompt: Optional[str] = None,
        tools: Optional[list[dict[str, Any]]] = None,
    ) -> genai.GenerativeModel:
        """Create a GenerativeModel with optional system instruction and tools."""
        kwargs: dict[str, Any] = {}
        if system_prompt:
            kwargs["system_instruction"] = system_prompt
        if tools:
            kwargs["tools"] = tools
        return genai.GenerativeModel(self._model_name, **kwargs)

    # -- public interface -------------------------------------------------

    async def analyse_image(
        self,
        image_base64: str,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Send an image with a prompt to Gemini's vision endpoint."""
        model = self._get_model(system_prompt=system_prompt)
        image_bytes = base64_to_bytes(image_base64)
        image_part = {"mime_type": "image/png", "data": image_bytes}
        response = await model.generate_content_async([prompt, image_part])
        
        # Track token usage
        self._track_usage(response, "analyse_image")
        
        return response.text

    async def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        system_prompt: Optional[str] = None,
        tools: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """Multi-turn conversation with optional tool definitions."""
        model = self._get_model(system_prompt=system_prompt, tools=tools)
        # Convert from OpenAI-style messages to Gemini content list
        contents = self._convert_messages(messages)
        response = await model.generate_content_async(contents)
        
        # Track token usage
        self._track_usage(response, "chat")
        
        return self._response_to_dict(response)

    async def complete(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Simple single-turn completion."""
        model = self._get_model(system_prompt=system_prompt)
        response = await model.generate_content_async(prompt)
        
        # Track token usage
        self._track_usage(response, "complete")
        
        return response.text

    # -- tracking helper --------------------------------------------------

    @staticmethod
    def _track_usage(response: Any, method: str = "") -> None:
        """Track token usage from API response."""
        tracker = get_tracker()
        if tracker and hasattr(response, "usage_metadata"):
            # Gemini uses usage_metadata instead of usage
            metadata = response.usage_metadata
            if hasattr(metadata, "prompt_token_count") and hasattr(metadata, "candidates_token_count"):
                tracker.add_input(metadata.prompt_token_count, method)
                tracker.add_output(metadata.candidates_token_count, method)

    # -- conversion helpers -----------------------------------------------

    @staticmethod
    def _convert_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convert generic message dicts to Gemini content format."""
        contents: list[dict[str, Any]] = []
        for msg in messages:
            role = "model" if msg.get("role") == "assistant" else "user"
            parts = []
            content = msg.get("content", "")
            if isinstance(content, str):
                parts.append({"text": content})
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        parts.append({"text": block["text"]})
            contents.append({"role": role, "parts": parts})
        return contents

    @staticmethod
    def _response_to_dict(response: Any) -> dict[str, Any]:
        """Normalise a Gemini response to a serialisable dict."""
        text_parts = []
        tool_calls = []
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, "text") and part.text:
                    text_parts.append({"type": "text", "text": part.text})
                if hasattr(part, "function_call") and part.function_call:
                    tool_calls.append(
                        {
                            "type": "tool_use",
                            "name": part.function_call.name,
                            "input": dict(part.function_call.args),
                        }
                    )
        content = text_parts + tool_calls
        return {"role": "assistant", "content": content}
