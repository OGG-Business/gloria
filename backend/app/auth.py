from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
import httpx
from .config import settings

security = HTTPBearer(auto_error=False)

_jwks: Optional[dict] = None


async def get_jwks() -> Optional[dict]:
    global _jwks
    if settings.oidc_issuer is None:
        return None
    if _jwks is None:
        async with httpx.AsyncClient(timeout=10) as client:
            jwks_uri = f"{settings.oidc_issuer.rstrip('/')}/.well-known/openid-configuration"
            r = await client.get(jwks_uri)
            r.raise_for_status()
            jwks_url = r.json().get("jwks_uri")
            jr = await client.get(jwks_url)
            jr.raise_for_status()
            _jwks = jr.json()
    return _jwks


async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    if settings.auth_disabled:
        return {"sub": "dev-user", "roles": ["user"]}
    if token is None:
        raise HTTPException(status_code=401, detail="Missing token")
    jwks = await get_jwks()
    if not jwks:
        raise HTTPException(status_code=500, detail="JWKS not configured")
    try:
        # For brevity, not selecting key by kid here; in prod use key selection
        unverified = jwt.get_unverified_header(token.credentials)
        claims = jwt.get_unverified_claims(token.credentials)
        if settings.oidc_audience and settings.oidc_audience not in claims.get("aud", []):
            raise HTTPException(status_code=401, detail="Invalid audience")
        # Skipping signature verification in this minimal scaffold; replace with key verify
        return claims
    except Exception as ex:
        raise HTTPException(status_code=401, detail=f"Invalid token: {ex}")


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    roles = user.get("roles", [])
    if "admin" not in roles and not settings.auth_disabled:
        raise HTTPException(status_code=403, detail="Admin only")
    return user