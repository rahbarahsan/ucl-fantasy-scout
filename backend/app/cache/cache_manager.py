"""Session-based in-memory cache manager for agent outputs."""

import json
import time
from typing import Any, Optional

from app.utils.logger import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Session-based cache for agent outputs (cleared on restart)."""

    def __init__(self):
        """Initialize in-memory cache store."""
        self._store: dict[str, dict[str, Any]] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        if key in self._store:
            self._hits += 1
            logger.info("cache_hit", key=key, hit_rate=f"{self.hit_rate():.1%}")
            return self._store[key]["value"]

        self._misses += 1
        logger.debug("cache_miss", key=key, hit_rate=f"{self.hit_rate():.1%}")
        return None

    def set(self, key: str, value: Any) -> None:
        """Store value in cache."""
        self._store[key] = {
            "value": value,
            "created_at": time.time(),
            "size_bytes": len(json.dumps(value, default=str)),
        }
        logger.info("cache_set", key=key, size_bytes=self._store[key]["size_bytes"])

    def delete(self, key: str) -> None:
        """Delete value from cache."""
        if key in self._store:
            del self._store[key]
            logger.info("cache_delete", key=key)

    def clear(self) -> None:
        """Clear entire cache."""
        self._store.clear()
        logger.info("cache_cleared")

    def hit_rate(self) -> float:
        """Return cache hit rate (0.0-1.0)."""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    def stats(self) -> dict[str, Any]:
        """Return cache statistics."""
        total_size = sum(v["size_bytes"] for v in self._store.values())
        return {
            "entries": len(self._store),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{self.hit_rate():.1%}",
            "total_size_bytes": total_size,
            "total_size_mb": total_size / 1024 / 1024,
        }

    def print_stats(self) -> None:
        """Print cache stats to console."""
        stats = self.stats()
        print("\n" + "=" * 70)
        print("CACHE STATISTICS")
        print("=" * 70)
        print(f"  Total Entries: {stats['entries']}")
        print(f"  Cache Hits: {stats['hits']}")
        print(f"  Cache Misses: {stats['misses']}")
        print(f"  Hit Rate: {stats['hit_rate']}")
        print(f"  Size: {stats['total_size_mb']:.2f} MB")
        print("=" * 70 + "\n")


# Global cache instance (session-based, cleared on restart)
cache_manager = CacheManager()
