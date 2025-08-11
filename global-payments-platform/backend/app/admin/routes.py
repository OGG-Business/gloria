from fastapi import APIRouter, Depends
from app.auth.security import require_roles
from app.connectors.psd2_bnp import BNPParibasPSD2Client

router = APIRouter()

@router.get("/status")
async def status(user=Depends(require_roles("admin", "operator"))):
    return {"ok": True}

@router.get("/psd2/prepaid")
async def psd2_prepaid(user=Depends(require_roles("admin", "operator"))):
    client = BNPParibasPSD2Client()
    resp = await client.prepaid_cards()
    return {"status_code": resp.status_code, "body": resp.text}