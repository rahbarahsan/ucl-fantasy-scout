"""Tests for the image utility module."""

import base64

from app.utils.image import (
    base64_to_bytes,
    bytes_to_base64,
    strip_data_uri,
    validate_base64_image,
)

# A tiny valid 1x1 PNG for testing
_TINY_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
    b"\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00"
    b"\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


class TestValidateBase64Image:
    """Tests for validate_base64_image."""

    def test_valid_png(self) -> None:
        """A valid PNG should return 'png'."""
        b64 = base64.b64encode(_TINY_PNG).decode()
        assert validate_base64_image(b64) == "png"

    def test_with_data_uri_prefix(self) -> None:
        """Data-URI-prefixed images should still validate."""
        b64 = base64.b64encode(_TINY_PNG).decode()
        data_uri = f"data:image/png;base64,{b64}"
        assert validate_base64_image(data_uri) == "png"

    def test_invalid_base64(self) -> None:
        """Garbage input should return None."""
        assert validate_base64_image("not-valid-base64!!!") is None

    def test_unsupported_format(self) -> None:
        """A valid Base64 string that is not an image should return None."""
        b64 = base64.b64encode(b"hello world").decode()
        assert validate_base64_image(b64) is None


class TestStripDataUri:
    """Tests for strip_data_uri."""

    def test_strips_prefix(self) -> None:
        """Data URI prefix should be removed."""
        assert strip_data_uri("data:image/png;base64,AAAA") == "AAAA"

    def test_no_prefix(self) -> None:
        """Plain Base64 should pass through unchanged."""
        assert strip_data_uri("AAAA") == "AAAA"


class TestRoundTrip:
    """Base64 encode/decode round trip."""

    def test_round_trip(self) -> None:
        """Bytes should survive a round trip through Base64."""
        data = b"hello world"
        assert base64_to_bytes(bytes_to_base64(data)) == data
