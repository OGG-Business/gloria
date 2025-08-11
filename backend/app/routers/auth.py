from fastapi import APIRouter
from ..core.config import settings

router = APIRouter()


@router.get("/config")
def auth_config():
    return {
        "issuer": settings.oidc_issuer,
        "audience": settings.oidc_audience,
        "dev_mode_no_auth": settings.dev_mode_no_auth,
    }