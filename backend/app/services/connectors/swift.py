import httpx
from typing import Dict
import ssl
import os

class SwiftConnector:
    def __init__(self, base_url: str, client_cert: str | None = None, client_key: str | None = None, ca_cert: str | None = None):
        self.base_url = base_url.rstrip('/')
        self.client_cert = client_cert
        self.client_key = client_key
        self.ca_cert = ca_cert

    def _client(self) -> httpx.AsyncClient:
        cert = None
        if self.client_cert and self.client_key:
            cert = (self.client_cert, self.client_key)
        verify = self.ca_cert or True
        return httpx.AsyncClient(base_url=self.base_url, cert=cert, verify=verify, timeout=30)

    async def send_credit_transfer(self, transfer: Dict, dry_run: bool = True) -> Dict:
        if dry_run:
            return {"status": "DRY_RUN", "message": "No message sent"}
        async with self._client() as client:
            r = await client.post("/payments", json=transfer)
            return {"status": r.status_code, "payload": r.json() if r.headers.get('content-type','').startswith('application/json') else await r.aread()}