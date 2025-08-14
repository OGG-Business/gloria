import httpx
import os
from typing import Dict, Any

class AzqoreConnector:
    """
    Connector for initiating payments through the AZQORE Service Bureau API.
    """
    def __init__(self, settings):
        self.settings = settings
        self.base_url = settings.connector_azqore_api_url
        self.bic = settings.connector_azqore_bic
        # The JWT token should be securely managed and rotated.
        # For this implementation, we read it from an environment variable.
        self.jwt_token = settings.connector_azqore_jwt_token
        if not self.jwt_token:
            raise ValueError("AZQORE JWT token is not configured.")

    async def _get_auth_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.jwt_token}",
            "X-BIC": self.bic,
            "Content-Type": "application/json",
        }

    async def get_quotation(self, amount: float, currency: str, beneficiary_bic: str) -> Dict[str, Any]:
        """
        Step 1: Get a quotation to lock in fees and exchange rates.
        """
        url = f"{self.base_url}/v1/quotations"
        payload = {
            "amount": amount,
            "currency": currency,
            "beneficiary_bic": beneficiary_bic
        }
        async with httpx.AsyncClient(timeout=20) as client:
            headers = await self._get_auth_headers()
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    async def create_transaction(self, quotation_id: str, beneficiary_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 2: Create a transaction against a quotation with full beneficiary details.
        """
        url = f"{self.base_url}/v1/quotations/{quotation_id}/transactions"
        async with httpx.AsyncClient(timeout=30) as client:
            headers = await self._get_auth_headers()
            response = await client.post(url, json=beneficiary_details, headers=headers)
            response.raise_for_status()
            return response.json()

    async def confirm_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        Step 3: Confirm the transaction to initiate the actual payment.
        """
        url = f"{self.base_url}/v1/transactions/{transaction_id}/confirm"
        async with httpx.AsyncClient(timeout=60) as client:
            headers = await self._get_auth_headers()
            response = await client.post(url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def get_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """
        (Optional) Poll for transaction status.
        """
        url = f"{self.base_url}/v1/transactions/{transaction_id}"
        async with httpx.AsyncClient(timeout=20) as client:
            headers = await self._get_auth_headers()
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
