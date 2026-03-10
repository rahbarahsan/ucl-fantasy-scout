"""POST /analyse — main squad analysis endpoint."""

from typing import Union

from fastapi import APIRouter, HTTPException, Request

from app.agents.pipeline import run_analysis
from app.api.middleware.auth import require_api_key
from app.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    MatchdayClarification,
)
from app.utils.image import strip_data_uri, validate_base64_image
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["analysis"])


@router.post(
    "/analyse",
    response_model=Union[AnalysisResponse, MatchdayClarification],
)
async def analyse_squad(
    body: AnalysisRequest,
    request: Request,
) -> Union[AnalysisResponse, MatchdayClarification]:
    """Analyse a UCL Fantasy squad screenshot and return verdicts."""
    # Validate image
    fmt = validate_base64_image(body.image_base64)
    if fmt is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid or unsupported image. Please upload a PNG, JPEG, or WebP.",
        )

    # Resolve API key
    api_key = require_api_key(request, provider=body.provider)

    image_data = strip_data_uri(body.image_base64)

    try:
        result = await run_analysis(
            image_base64=image_data,
            provider_name=body.provider,
            user_matchday=body.matchday,
            api_key=api_key,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pylint: disable=broad-except
        # Pipeline must not crash with an unhandled 500
        logger.error("analysis_pipeline_error", error=str(exc))
        raise HTTPException(
            status_code=500,
            detail="An error occurred during analysis. Please try again.",
        ) from exc

    return result
