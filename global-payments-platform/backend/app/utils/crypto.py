from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import os
import hvac
from app.config import get_settings

settings = get_settings()

class CryptoManager:
    def __init__(self):
        self.client = None
        try:
            self.client = hvac.Client(url=settings.vault_addr, token=settings.vault_token)
        except Exception:
            self.client = None

    def _derive_key(self, base_key: bytes) -> bytes:
        hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"payments-aes")
        return hkdf.derive(base_key)

    def encrypt(self, plaintext: bytes, aad: bytes | None = None) -> bytes:
        if self.client and self.client.is_authenticated():
            # Use Vault transit encrypt
            resp = self.client.secrets.transit.encrypt_data(
                name=settings.vault_transit_key, plaintext=plaintext
            )
            return resp["data"]["ciphertext"].encode()
        # Dev fallback: local AES-GCM
        base_key = os.environ.get("DEV_AES_KEY", os.urandom(32))
        if isinstance(base_key, str):
            base_key = base_key.encode()
        key = self._derive_key(base_key)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, plaintext, aad)
        return nonce + ct

    def decrypt(self, ciphertext: bytes, aad: bytes | None = None) -> bytes:
        if self.client and self.client.is_authenticated():
            resp = self.client.secrets.transit.decrypt_data(
                name=settings.vault_transit_key, ciphertext=ciphertext.decode()
            )
            return resp["data"]["plaintext"].encode()
        base_key = os.environ.get("DEV_AES_KEY", os.urandom(32))
        if isinstance(base_key, str):
            base_key = base_key.encode()
        key = self._derive_key(base_key)
        aesgcm = AESGCM(key)
        nonce, data = ciphertext[:12], ciphertext[12:]
        return aesgcm.decrypt(nonce, data, aad)

crypto_manager = CryptoManager()