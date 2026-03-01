"""E2E smoke test against the local server.

This test is designed to run manually before a release.
It hits the actual endpoints but uses a mock image.
"""

import base64

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

_TINY_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
    b"\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00"
    b"\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


class TestE2EHealth:
    """Basic health endpoint tests."""

    @pytest.mark.asyncio
    async def test_health_returns_ok(self) -> None:
        """GET /health should return 200."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"


class TestE2EAnalysis:
    """Analysis endpoint smoke tests."""

    @pytest.mark.asyncio
    async def test_analyse_missing_key_returns_401(self) -> None:
        """POST /api/analyse without a key should return 401."""
        image_b64 = base64.b64encode(_TINY_PNG).decode()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/analyse",
                json={
                    "image_base64": image_b64,
                    "provider": "anthropic",
                },
            )
        assert resp.status_code == 401
