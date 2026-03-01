"""Pydantic models for the /research ad-hoc endpoint."""

from typing import Literal

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    """Incoming request for ad-hoc research questions."""

    question: str = Field(
        ...,
        description="Free-form research question from the user.",
    )
    provider: Literal["anthropic", "gemini"] = Field(
        default="anthropic",
        description="Which AI provider to use.",
    )


class ResearchResponse(BaseModel):
    """Response to an ad-hoc research question."""

    answer: str
    sources: list[str] = Field(default_factory=list)
