import base64
import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
import httpx
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .core.config import settings

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(token: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)) -> str:
    if settings.dev_mode_no_auth:
        return "dev-user"
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    try:
        payload = await _verify_jwt(token.credentials)
        return payload.get("sub") or payload.get("email") or "anonymous"
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


async def _verify_jwt(token: str) -> dict:
    if not settings.oidc_issuer or not settings.oidc_audience:
        raise ValueError("OIDC not configured")
    jwks_url = settings.oidc_jwks_url or f"{settings.oidc_issuer}/.well-known/jwks.json"
    async with httpx.AsyncClient(timeout=5) as client:
        jwks = (await client.get(jwks_url)).json()
    header = jwt.get_unverified_header(token)
    key = next((k for k in jwks["keys"] if k["kid"] == header.get("kid")), None)
    if not key:
        raise ValueError("Invalid token kid")
    return jwt.decode(token, key, algorithms=[key.get("alg", "RS256")], audience=settings.oidc_audience, issuer=settings.oidc_issuer)


class KeyProvider:
    _cached_key: Optional[bytes] = None

    @classmethod
    def get_key(cls) -> bytes:
        if cls._cached_key:
            return cls._cached_key
        backend = settings.secrets_backend
        key_b64: Optional[str] = None
        if backend == "env":
            key_b64 = settings.app_master_key_b64
        elif backend == "vault":
            try:
                import hvac  # lazy import
            except Exception:
                raise RuntimeError("hvac package missing for Vault backend")
            client = hvac.Client(url=settings.vault_addr, token=settings.vault_token)
            secret = client.secrets.kv.v2.read_secret_version(path=settings.vault_kv_path.replace("secret/data/", ""))
            key_b64 = secret["data"]["data"].get(settings.vault_key_field)
        elif backend == "gsm":
            from google.cloud import secretmanager  # type: ignore
            if not settings.gcp_project_id:
                raise RuntimeError("GCP_PROJECT_ID missing for GSM backend")
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{settings.gcp_project_id}/secrets/{settings.gsm_secret_name}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            key_b64 = response.payload.data.decode("utf-8")
        else:
            raise RuntimeError(f"Unsupported secrets backend: {backend}")
        if not key_b64:
            raise RuntimeError("Master key not found")
        key = base64.b64decode(key_b64)
        if len(key) != 32:
            raise RuntimeError("Master key must be 32 bytes (AES-256)")
        cls._cached_key = key
        return key


def encrypt_blob(plaintext: bytes) -> str:
    key = KeyProvider.get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")


def decrypt_blob(b64_blob: str) -> bytes:
    key = KeyProvider.get_key()
    aesgcm = AESGCM(key)
    blob = base64.b64decode(b64_blob)
    nonce, ciphertext = blob[:12], blob[12:]
    return aesgcm.decrypt(nonce, ciphertext, None)