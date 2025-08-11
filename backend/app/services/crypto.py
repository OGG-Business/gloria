import os
from typing import Optional, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import constant_time
import secrets
import binascii
from ..config import settings


def _load_key() -> bytes:
    if settings.encryption_key_hex:
        return binascii.unhexlify(settings.encryption_key_hex)
    # Dev-only random ephemeral key
    return AESGCM.generate_key(bit_length=256)


def encrypt(plaintext: bytes, associated_data: Optional[bytes] = None) -> bytes:
    key = _load_key()
    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)
    ct = aesgcm.encrypt(nonce, plaintext, associated_data)
    return nonce + ct


def decrypt(ciphertext: bytes, associated_data: Optional[bytes] = None) -> bytes:
    key = _load_key()
    aesgcm = AESGCM(key)
    nonce = ciphertext[:12]
    ct = ciphertext[12:]
    return aesgcm.decrypt(nonce, ct, associated_data)


def constant_time_equals(a: bytes, b: bytes) -> bool:
    return constant_time.bytes_eq(a, b)