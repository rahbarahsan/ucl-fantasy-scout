"""Helpers for generating unique cache keys."""

from __future__ import annotations

import re
import uuid

_SLUG_REGEX = re.compile(r"[^a-z0-9]+")


def _slugify(value: str) -> str:
    """Convert arbitrary text into a safe, readable slug."""
    lowered = value.lower()
    replaced = _SLUG_REGEX.sub("-", lowered)
    stripped = replaced.strip("-")
    return stripped or "data"


def build_cache_key(namespace: str, *parts: str | None) -> str:
    """Return a unique cache key with a readable namespace and random suffix."""
    normalized_parts = []
    for part in parts:
        if part is None:
            continue
        text = str(part).strip()
        if not text:
            continue
        normalized_parts.append(_slugify(text))

    slug_section = ":".join(normalized_parts) if normalized_parts else "data"
    namespace = namespace.rstrip(":")
    suffix = uuid.uuid4().hex[:8]
    return f"{namespace}:{slug_section}:{suffix}"
