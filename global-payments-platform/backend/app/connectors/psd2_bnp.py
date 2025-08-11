import httpx
from app.config import get_settings

settings = get_settings()

class BNPParibasPSD2Client:
    def __init__(self):
        self.base_url = settings.psd2_base_url.rstrip('/')
        self.api_key_header = settings.psd2_api_key_header_name
        self.api_key_value = settings.psd2_api_key_value
        self.cert = (settings.psd2_tls_client_cert_path, settings.psd2_tls_client_key_path)
        self.verify = settings.psd2_tls_ca_chain_path
        if not self.api_key_value:
            raise RuntimeError("PSD2 API key is not configured")

    async def prepaid_cards(self, path: str = "/v1/cards/prepaid") -> httpx.Response:
        headers = {self.api_key_header: self.api_key_value}
        async with httpx.AsyncClient(verify=self.verify, cert=self.cert, timeout=60) as client:
            resp = await client.get(self.base_url + path, headers=headers)
            resp.raise_for_status()
            return resp