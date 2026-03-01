"""Pydantic models for the /analyse endpoint."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """Incoming request body for squad analysis."""

    image_base64: str = Field(
        ...,
        description="Base64-encoded squad screenshot (with or without data-URI prefix).",
    )
    matchday: Optional[str] = Field(
        default=None,
        description="Manually provided matchday identifier, e.g. 'Matchday 5'.",
    )
    provider: Literal["anthropic", "gemini"] = Field(
        default="anthropic",
        description="Which AI provider to use for this request.",
    )


class Alternative(BaseModel):
    """A suggested replacement for a RISK / BENCH player."""

    name: str
    team: str
    position: str
    price: str
    reason: str


class PlayerResult(BaseModel):
    """Analysis verdict for a single player."""

    name: str
    position: Literal["GK", "DEF", "MID", "FWD"]
    team: str
    status: Literal["START", "RISK", "BENCH"]
    reason: str
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    price: str
    is_substitute: bool = False
    alternatives: list[Alternative] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    """Full analysis report returned to the frontend."""

    matchday: str
    matchday_confirmed: bool = False
    analysis_day: Literal["DAY_1", "DAY_2", "BOTH"] = "BOTH"
    early_warning: bool = False
    players: list[PlayerResult] = Field(default_factory=list)


class MatchdayClarification(BaseModel):
    """Returned when the matchday could not be determined from the image."""

    needs_clarification: bool = True
    message: str = (
        "We could not confirm the matchday from your screenshot. Could you tell us which matchday this is?"
    )
