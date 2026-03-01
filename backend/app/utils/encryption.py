"""AES-256 encryption utilities for API key handling."""

import base64
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

from app.config import settings

_KEY_BYTES = 32
_IV_BYTES = 16
_BLOCK_BITS = 128


def _derive_key() -> bytes:
    """Derive a 32-byte key from the configured encryption secret."""
    secret = settings.encryption_secret.encode("utf-8")
    # Pad or truncate to exactly 32 bytes
    return secret.ljust(_KEY_BYTES, b"\0")[:_KEY_BYTES]


def encrypt(plaintext: str) -> str:
    """Encrypt *plaintext* and return a Base64-encoded ``iv:ciphertext`` string."""
    key = _derive_key()
    init_vector = os.urandom(_IV_BYTES)

    padder = PKCS7(_BLOCK_BITS).padder()
    padded = padder.update(plaintext.encode("utf-8")) + padder.finalize()

    cipher = Cipher(
        algorithms.AES(key), modes.CBC(init_vector), backend=default_backend()
    )
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()

    iv_b64 = base64.b64encode(init_vector).decode("utf-8")
    ct_b64 = base64.b64encode(ciphertext).decode("utf-8")
    return f"{iv_b64}:{ct_b64}"


def decrypt(token: str) -> str:
    """Decrypt a Base64-encoded ``iv:ciphertext`` token back to plaintext."""
    key = _derive_key()
    iv_b64, ct_b64 = token.split(":")
    init_vector = base64.b64decode(iv_b64)
    ciphertext = base64.b64decode(ct_b64)

    cipher = Cipher(
        algorithms.AES(key), modes.CBC(init_vector), backend=default_backend()
    )
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = PKCS7(_BLOCK_BITS).unpadder()
    plaintext = unpadder.update(padded) + unpadder.finalize()
    return plaintext.decode("utf-8")
