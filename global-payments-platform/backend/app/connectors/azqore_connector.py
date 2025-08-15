import httpx
import os
from typing import Dict, Any
from app.auth.keycloak_service import KeycloakService

class AzqoreConnector:
    """
    Connector for initiating payments through the AZQORE Service Bureau API.
    It uses Keycloak to dynamically fetch bearer tokens.
    """
    def __init__(self, settings):
        self.settings = settings
        self.base_url = settings.connector_azqore_api_url
        self.bic = settings.connector_azqore_bic
        # Instantiate the Keycloak service to handle token fetching
        self.keycloak_service = KeycloakService(settings)

    async def _get_auth_headers(self) -> Dict[str, str]:
        """
        Dynamically fetches a JWT from Keycloak and prepares the auth headers.
        """
        # Get a fresh (or cached) token from our service
        jwt_token = await self.keycloak_service.get_access_token()

        return {
            "Authorization": f"Bearer {jwt_token}",
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
