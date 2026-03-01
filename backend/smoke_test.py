#!/usr/bin/env python
"""Smoke test: verify API key loading and basic connectivity."""

import asyncio

from app.config import settings
from app.providers.anthropic import AnthropicProvider


async def main():
    print("=" * 60)
    print("SMOKE TEST: UCL Fantasy Scout Backend")
    print("=" * 60)

    # 1. Check config loading
    print("\n✓ Checking environment configuration...")
    print(f"  - Anthropic Key: {'LOADED' if settings.anthropic_api_key else 'MISSING'}")
    if settings.anthropic_api_key:
        print(f"    Key prefix: {settings.anthropic_api_key[:20]}...")
    print(
        f"  - Encryption Secret: {'LOADED' if settings.encryption_secret else 'MISSING'}"
    )
    print(f"  - Environment: {settings.environment}")

    # 2. Test Anthropic provider instantiation
    if not settings.anthropic_api_key:
        print("\n✗ Cannot test Anthropic provider: API key missing")
        return

    print("\n✓ Initializing Anthropic provider...")
    try:
        provider = AnthropicProvider(api_key=settings.anthropic_api_key)
        print("  ✓ Provider initialized successfully")
    except Exception as e:
        print(f"  ✗ Failed to initialize provider: {e}")
        return

    # 3. Test a simple completion call
    print("\n✓ Testing API call (simple completion)...")
    try:
        result = await provider.complete("Tell me one thing about UCL in 10 words max.")
        print(f"  ✓ API call successful!")
        print(f"  Response: {result[:100]}...")
    except Exception as e:
        print(f"  ✗ API call failed: {e}")
        return

    print("\n" + "=" * 60)
    print("✓ All smoke tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
