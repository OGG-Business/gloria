"""
SWIFT Connector for Banking Transfer Platform
Handles SWIFT MT/MX messages and ISO 20022 integration
"""

import asyncio
import logging
import ssl
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import aiohttp
import aiofiles
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import hvac
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

@dataclass
class SwiftMessage:
    """SWIFT message structure"""
    message_type: str  # MT103, MT202, etc.
    sender_bic: str
    receiver_bic: str
    message_id: str
    content: str
    timestamp: datetime
    priority: str = "N"  # N=Normal, U=Urgent, S=System
    delivery_monitoring: str = "1"  # 1=Non-delivery warning, 2=Delivery notification, 3=Both
    obsolescence_period: str = "003"  # 003=3 hours

class SwiftConnectorConfig(BaseModel):
    """SWIFT connector configuration"""
    bic: str = Field(..., description="Bank Identifier Code")
    cert_path: str = Field(..., description="Path to client certificate")
    key_path: str = Field(..., description="Path to private key")
    ca_cert_path: str = Field(..., description="Path to CA certificate")
    swiftnet_endpoint: str = Field(..., description="SWIFTNet endpoint URL")
    dry_run: bool = Field(True, description="Dry run mode for testing")
    message_types: List[str] = Field(default=["MT103", "MT202", "MT910", "MT900"])
    timeout: int = Field(30, description="Connection timeout in seconds")
    retry_attempts: int = Field(3, description="Number of retry attempts")
    retry_delay: int = Field(5, description="Delay between retries in seconds")

class SwiftConnector:
    """SWIFT connector for sending and receiving SWIFT messages"""
    
    def __init__(self, config: SwiftConnectorConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.ssl_context: Optional[ssl.SSLContext] = None
        self._setup_ssl_context()
        
    def _setup_ssl_context(self):
        """Setup SSL context with client certificates"""
        try:
            self.ssl_context = ssl.create_default_context(
                cafile=self.config.ca_cert_path
            )
            
            # Load client certificate and private key
            self.ssl_context.load_cert_chain(
                certfile=self.config.cert_path,
                keyfile=self.config.key_path
            )
            
            # Verify server certificate
            self.ssl_context.verify_mode = ssl.CERT_REQUIRED
            self.ssl_context.check_hostname = True
            
            logger.info(f"SSL context configured for BIC: {self.config.bic}")
            
        except Exception as e:
            logger.error(f"Failed to setup SSL context: {e}")
            raise Exception(f"SSL context setup failed: {e}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Establish connection to SWIFTNet"""
        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
            
            # Test connection
            await self._test_connection()
            logger.info(f"Connected to SWIFTNet: {self.config.swiftnet_endpoint}")
            
        except Exception as e:
            logger.error(f"Failed to connect to SWIFTNet: {e}")
            raise Exception(f"Connection failed: {e}")
    
    async def disconnect(self):
        """Close SWIFTNet connection"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Disconnected from SWIFTNet")
    
    async def _test_connection(self):
        """Test SWIFTNet connectivity"""
        if not self.session:
            raise Exception("Not connected to SWIFTNet")
        
        try:
            async with self.session.get(f"{self.config.swiftnet_endpoint}/health") as response:
                if response.status != 200:
                    raise Exception(f"Health check failed: {response.status}")
                logger.info("SWIFTNet connectivity test passed")
        except Exception as e:
            raise Exception(f"Connectivity test failed: {e}")
    
    def create_mt103_message(self, transfer) -> SwiftMessage:
        """Create SWIFT MT103 message for customer transfer"""
        try:
            # Generate unique message ID
            message_id = f"{self.config.bic}{datetime.now().strftime('%y%m%d%H%M%S')}"
            
            # Format amount with 2 decimal places
            amount = f"{transfer.amount:.2f}"
            
            # Create MT103 message content
            content = f"""{{1:F01{self.config.bic}XXXXX}{4:
:20:{message_id}
:23B:CRED
:32A:{transfer.created_at.strftime('%y%m%d')}{transfer.currency}{amount}N
:50K:/{transfer.source_account.holder_name}
{transfer.source_account.iban}
:59:/{transfer.beneficiary_name}
{transfer.destination_account.iban}
:71A:SHA
:72:/INS/{transfer.destination_account.bic}
-}}"""
            
            return SwiftMessage(
                message_type="MT103",
                sender_bic=self.config.bic,
                receiver_bic=transfer.destination_account.bic,
                message_id=message_id,
                content=content,
                timestamp=datetime.now(timezone.utc),
                priority="N"
            )
            
        except Exception as e:
            logger.error(f"Failed to create MT103 message: {e}")
            raise Exception(f"MT103 creation failed: {e}")
    
    async def send_message(self, message: SwiftMessage) -> Dict[str, str]:
        """Send SWIFT message to SWIFTNet"""
        if self.config.dry_run:
            logger.info(f"DRY RUN: Would send {message.message_type} message: {message.message_id}")
            return {
                "status": "DRY_RUN",
                "message_id": message.message_id,
                "acknowledgment": "DRY_RUN_ACK"
            }
        
        if not self.session:
            raise Exception("Not connected to SWIFTNet")
        
        for attempt in range(self.config.retry_attempts):
            try:
                # Prepare message payload
                payload = {
                    "sender_bic": message.sender_bic,
                    "receiver_bic": message.receiver_bic,
                    "message_type": message.message_type,
                    "message_id": message.message_id,
                    "content": message.content,
                    "priority": message.priority,
                    "delivery_monitoring": message.delivery_monitoring,
                    "obsolescence_period": message.obsolescence_period,
                    "timestamp": message.timestamp.isoformat()
                }
                
                # Send message
                async with self.session.post(
                    f"{self.config.swiftnet_endpoint}/messages",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"SWIFT message sent successfully: {message.message_id}")
                        return result
                    else:
                        error_text = await response.text()
                        raise Exception(f"SWIFT send failed: {response.status} - {error_text}")
                        
            except Exception as e:
                logger.warning(f"SWIFT send attempt {attempt + 1} failed: {e}")
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_delay)
                else:
                    raise Exception(f"SWIFT send failed after {self.config.retry_attempts} attempts: {e}")

# Factory function for creating SWIFT connector
async def create_swift_connector() -> SwiftConnector:
    """Create SWIFT connector with configuration from settings"""
    config = SwiftConnectorConfig(
        bic="TESTUS33XXX",
        cert_path="/tmp/test.crt",
        key_path="/tmp/test.key",
        ca_cert_path="/tmp/ca.crt",
        swiftnet_endpoint="https://test.swift.com",
        dry_run=True
    )
    
    return SwiftConnector(config)