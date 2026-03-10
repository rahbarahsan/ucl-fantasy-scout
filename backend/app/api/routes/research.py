"""POST /research — ad-hoc research question endpoint."""

from fastapi import APIRouter, HTTPException, Request

from app.api.middleware.auth import resolve_api_key
from app.config import settings
from app.providers.anthropic import AnthropicProvider
from app.providers.gemini import GeminiProvider
from app.schemas.research import ResearchRequest, ResearchResponse
from app.tools.web_search import web_search
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["research"])

_SYSTEM_PROMPT = """\
You are a UCL Champions League football research assistant.
Answer the user's question using your knowledge and any web search results
provided. Be concise, accurate, and cite sources where possible.
If you are unsure, say so — do not fabricate information.
"""


@router.post("/research", response_model=ResearchResponse)
async def research_question(
    body: ResearchRequest,
    request: Request,
) -> ResearchResponse:
    """Answer a free-form UCL Fantasy research question."""
    api_key = resolve_api_key(request, provider=body.provider)
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail=(
                f"No {body.provider} API key available. "
                "Please configure it in settings."
            ),
        )

    # Gather web context
    results = await web_search(
        body.question,
        num_results=5,
        recency_days=7,
        serpapi_key=settings.serpapi_key,
    )
    context_lines = [f"[{r['title']}] {r['snippet']} ({r['link']})" for r in results]
    web_context = "\n".join(context_lines) if context_lines else "No web results."

    prompt = f"Web search results:\n{web_context}\n\n" f"User question: {body.question}"

    try:
        if body.provider == "anthropic":
            provider = AnthropicProvider(api_key=api_key)
        else:
            provider = GeminiProvider(api_key=api_key)

        answer = await provider.complete(prompt, system_prompt=_SYSTEM_PROMPT)
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("research_error", error=str(exc))
        raise HTTPException(
            status_code=500,
            detail="Research query failed. Please try again.",
        ) from exc

    sources = [r["link"] for r in results if r.get("link")]
    return ResearchResponse(answer=answer, sources=sources)
