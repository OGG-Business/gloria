import httpx
import time
from typing import Optional, Dict, Any

class KeycloakService:
    """
    Service to interact with Keycloak and fetch OAuth2 tokens.
    """
    def __init__(self, settings):
        self.settings = settings
        self.token_url = f"{settings.oidc_issuer_url}/protocol/openid-connect/token"
        self.client_id = settings.keycloak_azqore_client_id
        self.client_secret = settings.keycloak_azqore_client_secret

        # In-memory cache for the token
        self._cached_token: Optional[str] = None
        self._token_expiry_time: int = 0

    async def get_access_token(self) -> str:
        """
        Retrieves an access token from Keycloak, using a cached token if available and not expired.
        """
        # Check if cached token is still valid (with a 30-second buffer)
        if self._cached_token and self._token_expiry_time > (time.time() + 30):
            return self._cached_token

        # If not, fetch a new token
        return await self._fetch_new_token()

    async def _fetch_new_token(self) -> str:
        """
        Fetches a new access token from the Keycloak token endpoint.
        """
        if not self.client_id or not self.client_secret:
            raise ValueError("Keycloak client ID or secret is not configured.")

        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=payload, headers=headers)
            response.raise_for_status()
            token_data = response.json()

            access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 300) # Default to 5 minutes

            if not access_token:
                raise ValueError("Failed to retrieve access token from Keycloak response.")

            # Cache the new token and its expiry time
            self._cached_token = access_token
            self._token_expiry_time = time.time() + expires_in

            return self._cached_token
