import httpx
from typing import Dict

class MojaloopConnector:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    async def send_credit_transfer(self, transfer: Dict, dry_run: bool = True) -> Dict:
        if dry_run:
            return {"status": "DRY_RUN", "message": "No message sent"}
        async with httpx.AsyncClient(base_url=self.base_url, timeout=30) as client:
            r = await client.post("/transfers", json=transfer)
            return {"status": r.status_code, "payload": r.json()}