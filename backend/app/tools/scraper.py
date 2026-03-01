"""Lightweight scraper for known football-preview sources."""

from typing import Optional

import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)

_TIMEOUT = 12
_MAX_BODY = 200_000  # chars — we only need the article text, not entire pages


async def fetch_article_text(url: str) -> Optional[str]:
    """Fetch *url* and return a trimmed plain-text body.

    Returns ``None`` on any failure.  This is a best-effort utility —
    agents should never rely on scraping alone.
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        }
        async with httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            text = resp.text[:_MAX_BODY]
    except httpx.HTTPError as exc:
        logger.warning("scrape_failed", url=url, error=str(exc))
        return None

    # Strip HTML tags in a very rough way — good enough for AI consumption
    return _rough_strip_html(text)


def _rough_strip_html(html: str) -> str:
    """Remove HTML tags crudely, returning readable-ish text."""
    import re  # pylint: disable=import-outside-toplevel

    text = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.IGNORECASE)
    text = re.sub(r"<style[\s\S]*?</style>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
