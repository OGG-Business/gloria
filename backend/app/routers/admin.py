from fastapi import APIRouter, Depends
from ..auth import require_admin
from ..services.audit import get_audit_tail

router = APIRouter()


@router.get("/audit")
def audit_tail(n: int = 50, _=Depends(require_admin)):
    return get_audit_tail(n)