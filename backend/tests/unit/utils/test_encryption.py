"""Tests for the encryption utility module."""

import pytest

from app.utils.encryption import decrypt, encrypt


class TestEncryption:
    """Encryption round-trip and edge-case tests."""

    def test_encrypt_decrypt_round_trip(self) -> None:
        """Encrypted text should decrypt back to the original."""
        original = "sk-ant-test-key-12345"
        token = encrypt(original)
        assert decrypt(token) == original

    def test_different_plaintexts_produce_different_tokens(self) -> None:
        """Two different strings must not produce the same token."""
        token_a = encrypt("key-alpha")
        token_b = encrypt("key-beta")
        assert token_a != token_b

    def test_encrypt_empty_string(self) -> None:
        """Empty string should encrypt and decrypt cleanly."""
        token = encrypt("")
        assert decrypt(token) == ""

    def test_encrypt_unicode(self) -> None:
        """Unicode characters should survive the round trip."""
        original = "clé-secrète-🔑"
        token = encrypt(original)
        assert decrypt(token) == original

    def test_invalid_token_raises(self) -> None:
        """A corrupt token should raise an exception."""
        with pytest.raises(Exception):
            decrypt("not-a-valid-token")
