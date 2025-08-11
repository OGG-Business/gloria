"""
Mojaloop Connector for Banking Transfer Platform
Handles African corridors and real-time transfers
"""

import asyncio
import logging
import json
import hmac
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import aiohttp
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

@dataclass
class MojaloopTransfer:
    """Mojaloop transfer structure"""
    transfer_id: str
    quote_id: str
    payer_party_id: str
    payee_party_id: str
    amount: float
    currency: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

class MojaloopConnectorConfig(BaseModel):
    """Mojaloop connector configuration"""
    endpoint: str = Field(..., description="Mojaloop API endpoint")
    participant_id: str = Field(..., description="Participant ID")
    api_key: str = Field(..., description="API key for authentication")
    dry_run: bool = Field(True, description="Dry run mode for testing")
    timeout: int = Field(30, description="Connection timeout in seconds")
    retry_attempts: int = Field(3, description="Number of retry attempts")
    retry_delay: int = Field(5, description="Delay between retries in seconds")

class MojaloopConnector:
    """Mojaloop connector for African corridors"""
    
    def __init__(self, config: MojaloopConnectorConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Establish connection to Mojaloop"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.config.api_key,
                    "X-Participant-ID": self.config.participant_id
                }
            )
            
            # Test connection
            await self._test_connection()
            logger.info(f"Connected to Mojaloop: {self.config.endpoint}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Mojaloop: {e}")
            raise Exception(f"Connection failed: {e}")
    
    async def disconnect(self):
        """Close Mojaloop connection"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Disconnected from Mojaloop")
    
    async def _test_connection(self):
        """Test Mojaloop connectivity"""
        if not self.session:
            raise Exception("Not connected to Mojaloop")
        
        try:
            async with self.session.get(f"{self.config.endpoint}/health") as response:
                if response.status != 200:
                    raise Exception(f"Health check failed: {response.status}")
                logger.info("Mojaloop connectivity test passed")
        except Exception as e:
            raise Exception(f"Connectivity test failed: {e}")
    
    async def create_quote(self, transfer) -> Dict[str, Any]:
        """Create quote for transfer"""
        if self.config.dry_run:
            logger.info(f"DRY RUN: Would create quote for transfer: {transfer.transfer_id}")
            return {
                "quoteId": f"DRY_RUN_QUOTE_{transfer.transfer_id}",
                "transferAmount": {
                    "amount": str(transfer.amount),
                    "currency": transfer.currency
                },
                "payeeReceiveAmount": {
                    "amount": str(transfer.amount),
                    "currency": transfer.currency
                },
                "payeeFspFee": {
                    "amount": "0.00",
                    "currency": transfer.currency
                },
                "payeeFspCommission": {
                    "amount": "0.00",
                    "currency": transfer.currency
                },
                "expiration": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
            }
        
        try:
            payload = {
                "quoteId": f"QUOTE_{transfer.transfer_id}",
                "transactionId": transfer.transfer_id,
                "transactionRequestId": transfer.transfer_id,
                "payer": {
                    "partyIdType": "MSISDN",
                    "partyIdentifier": transfer.source_account.account_number
                },
                "payee": {
                    "partyIdType": "MSISDN",
                    "partyIdentifier": transfer.destination_account.account_number
                },
                "amountType": "SEND",
                "amount": {
                    "amount": str(transfer.amount),
                    "currency": transfer.currency
                },
                "transactionType": {
                    "scenario": "TRANSFER",
                    "subScenario": "TRANSFER",
                    "initiator": "PAYER",
                    "initiatorType": "CONSUMER"
                }
            }
            
            async with self.session.post(
                f"{self.config.endpoint}/quotes",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Quote created successfully: {result['quoteId']}")
                    return result
                else:
                    error_text = await response.text()
                    raise Exception(f"Quote creation failed: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"Failed to create quote: {e}")
            raise Exception(f"Quote creation failed: {e}")
    
    async def initiate_transfer(self, transfer, quote_id: str) -> Dict[str, Any]:
        """Initiate transfer using quote"""
        if self.config.dry_run:
            logger.info(f"DRY RUN: Would initiate transfer: {transfer.transfer_id}")
            return {
                "transferId": f"DRY_RUN_TRANSFER_{transfer.transfer_id}",
                "quoteId": quote_id,
                "status": "COMPLETED",
                "completedTimestamp": datetime.now(timezone.utc).isoformat()
            }
        
        try:
            payload = {
                "transferId": transfer.transfer_id,
                "quoteId": quote_id,
                "payer": {
                    "partyIdType": "MSISDN",
                    "partyIdentifier": transfer.source_account.account_number
                },
                "payee": {
                    "partyIdType": "MSISDN",
                    "partyIdentifier": transfer.destination_account.account_number
                },
                "amountType": "SEND",
                "currency": transfer.currency,
                "amount": str(transfer.amount),
                "transactionType": {
                    "scenario": "TRANSFER",
                    "subScenario": "TRANSFER",
                    "initiator": "PAYER",
                    "initiatorType": "CONSUMER"
                },
                "note": transfer.description
            }
            
            async with self.session.post(
                f"{self.config.endpoint}/transfers",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Transfer initiated successfully: {result['transferId']}")
                    return result
                else:
                    error_text = await response.text()
                    raise Exception(f"Transfer initiation failed: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"Failed to initiate transfer: {e}")
            raise Exception(f"Transfer initiation failed: {e}")

# Factory function for creating Mojaloop connector
async def create_mojaloop_connector() -> MojaloopConnector:
    """Create Mojaloop connector with configuration from settings"""
    config = MojaloopConnectorConfig(
        endpoint="https://test.mojaloop.io",
        participant_id="test-participant",
        api_key="test-api-key",
        dry_run=True
    )
    
    return MojaloopConnector(config)