from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
import httpx
from functools import lru_cache
from app.config import get_settings

security = HTTPBearer()
settings = get_settings()

@lru_cache
def _jwks() -> Dict[str, Any]:
    jwks_url = f"{settings.oidc_issuer_url}/.well-known/openid-configuration"
    with httpx.Client(timeout=10) as client:
        oidc = client.get(jwks_url).json()
        jwks_uri = oidc["jwks_uri"]
        jwks = client.get(jwks_uri).json()
        return jwks


def _get_public_key(token: str) -> Optional[Dict[str, Any]]:
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")
    for key in _jwks()["keys"]:
        if key.get("kid") == kid:
            return key
    return None


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    if not creds.scheme.lower() == "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth scheme")
    token = creds.credentials
    key = _get_public_key(token)
    if not key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWKS key not found")
    try:
        payload = jwt.decode(token, key, audience=settings.oidc_audience, options={"verify_aud": True})
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    roles = (
        payload.get("realm_access", {}).get("roles", [])
        or payload.get("resource_access", {}).get(settings.oidc_audience, {}).get("roles", [])
    )
    return {"sub": payload.get("sub"), "email": payload.get("email"), "roles": roles}


def require_roles(*required_roles: str):
    def _inner(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if not set(required_roles).intersection(set(user.get("roles", []))):
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return _inner