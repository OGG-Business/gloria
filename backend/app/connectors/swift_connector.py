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

from app.config import get_settings
from app.common.monitoring import record_swift_message
from app.transfers.models import Transfer, TransferStatus
from app.common.exceptions import SwiftConnectionError, SwiftMessageError

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
            raise SwiftConnectionError(f"SSL context setup failed: {e}")
    
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
            raise SwiftConnectionError(f"Connection failed: {e}")
    
    async def disconnect(self):
        """Close SWIFTNet connection"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Disconnected from SWIFTNet")
    
    async def _test_connection(self):
        """Test SWIFTNet connectivity"""
        if not self.session:
            raise SwiftConnectionError("Not connected to SWIFTNet")
        
        try:
            async with self.session.get(f"{self.config.swiftnet_endpoint}/health") as response:
                if response.status != 200:
                    raise SwiftConnectionError(f"Health check failed: {response.status}")
                logger.info("SWIFTNet connectivity test passed")
        except Exception as e:
            raise SwiftConnectionError(f"Connectivity test failed: {e}")
    
    def create_mt103_message(self, transfer: Transfer) -> SwiftMessage:
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
            raise SwiftMessageError(f"MT103 creation failed: {e}")
    
    def create_mt202_message(self, transfer: Transfer) -> SwiftMessage:
        """Create SWIFT MT202 message for bank transfer"""
        try:
            message_id = f"{self.config.bic}{datetime.now().strftime('%y%m%d%H%M%S')}"
            amount = f"{transfer.amount:.2f}"
            
            content = f"""{{1:F01{self.config.bic}XXXXX}{4:
:20:{message_id}
:21:{transfer.swift_message_id}
:32A:{transfer.created_at.strftime('%y%m%d')}{transfer.currency}{amount}N
:52A:{self.config.bic}
:53A:{transfer.source_account.bic}
:57A:{transfer.destination_account.bic}
:58A:/{transfer.destination_account.iban}
{transfer.destination_account.holder_name}
:71A:SHA
-}}"""
            
            return SwiftMessage(
                message_type="MT202",
                sender_bic=self.config.bic,
                receiver_bic=transfer.destination_account.bic,
                message_id=message_id,
                content=content,
                timestamp=datetime.now(timezone.utc),
                priority="N"
            )
            
        except Exception as e:
            logger.error(f"Failed to create MT202 message: {e}")
            raise SwiftMessageError(f"MT202 creation failed: {e}")
    
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
            raise SwiftConnectionError("Not connected to SWIFTNet")
        
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
                        record_swift_message(message.message_type, "sent", "success")
                        return result
                    else:
                        error_text = await response.text()
                        raise SwiftMessageError(f"SWIFT send failed: {response.status} - {error_text}")
                        
            except Exception as e:
                logger.warning(f"SWIFT send attempt {attempt + 1} failed: {e}")
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_delay)
                else:
                    record_swift_message(message.message_type, "sent", "failed")
                    raise SwiftMessageError(f"SWIFT send failed after {self.config.retry_attempts} attempts: {e}")
    
    async def receive_messages(self) -> List[SwiftMessage]:
        """Receive SWIFT messages from SWIFTNet"""
        if not self.session:
            raise SwiftConnectionError("Not connected to SWIFTNet")
        
        try:
            async with self.session.get(f"{self.config.swiftnet_endpoint}/messages") as response:
                if response.status == 200:
                    messages_data = await response.json()
                    messages = []
                    
                    for msg_data in messages_data:
                        message = SwiftMessage(
                            message_type=msg_data["message_type"],
                            sender_bic=msg_data["sender_bic"],
                            receiver_bic=msg_data["receiver_bic"],
                            message_id=msg_data["message_id"],
                            content=msg_data["content"],
                            timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                            priority=msg_data.get("priority", "N")
                        )
                        messages.append(message)
                        record_swift_message(message.message_type, "received", "success")
                    
                    logger.info(f"Received {len(messages)} SWIFT messages")
                    return messages
                else:
                    raise SwiftMessageError(f"Failed to receive messages: {response.status}")
                    
        except Exception as e:
            logger.error(f"Failed to receive SWIFT messages: {e}")
            raise SwiftMessageError(f"Message reception failed: {e}")
    
    def parse_iso20022_message(self, xml_content: str) -> Dict[str, any]:
        """Parse ISO 20022 message (pacs.008, pacs.002, etc.)"""
        try:
            root = ET.fromstring(xml_content)
            
            # Extract namespace
            ns = {'ns': root.tag.split('}')[0].strip('{')}
            
            # Parse based on message type
            if 'pacs.008' in root.tag:
                return self._parse_pacs008(root, ns)
            elif 'pacs.002' in root.tag:
                return self._parse_pacs002(root, ns)
            elif 'pacs.004' in root.tag:
                return self._parse_pacs004(root, ns)
            else:
                raise SwiftMessageError(f"Unsupported ISO 20022 message type: {root.tag}")
                
        except Exception as e:
            logger.error(f"Failed to parse ISO 20022 message: {e}")
            raise SwiftMessageError(f"ISO 20022 parsing failed: {e}")
    
    def _parse_pacs008(self, root: ET.Element, ns: Dict[str, str]) -> Dict[str, any]:
        """Parse pacs.008 (Customer Credit Transfer) message"""
        try:
            # Extract basic information
            msg_id = root.find('.//ns:MsgId', ns).text if root.find('.//ns:MsgId', ns) is not None else None
            cre_dt_tm = root.find('.//ns:CreDtTm', ns).text if root.find('.//ns:CreDtTm', ns) is not None else None
            
            # Extract transfer information
            instr_id = root.find('.//ns:InstrId', ns).text if root.find('.//ns:InstrId', ns) is not None else None
            end_to_end_id = root.find('.//ns:EndToEndId', ns).text if root.find('.//ns:EndToEndId', ns) is not None else None
            
            # Extract amount and currency
            amount_elem = root.find('.//ns:IntrBkSttlmAmt', ns)
            amount = float(amount_elem.text) if amount_elem is not None else None
            currency = amount_elem.get('Ccy') if amount_elem is not None else None
            
            # Extract account information
            dbtr_acct = root.find('.//ns:DbtrAcct', ns)
            cdtr_acct = root.find('.//ns:CdtrAcct', ns)
            
            dbtr_iban = None
            cdtr_iban = None
            
            if dbtr_acct is not None:
                iban_elem = dbtr_acct.find('.//ns:Id/ns:Othr/ns:Id', ns)
                dbtr_iban = iban_elem.text if iban_elem is not None else None
                
            if cdtr_acct is not None:
                iban_elem = cdtr_acct.find('.//ns:Id/ns:Othr/ns:Id', ns)
                cdtr_iban = iban_elem.text if iban_elem is not None else None
            
            return {
                "message_type": "pacs.008",
                "message_id": msg_id,
                "creation_datetime": cre_dt_tm,
                "instruction_id": instr_id,
                "end_to_end_id": end_to_end_id,
                "amount": amount,
                "currency": currency,
                "debtor_iban": dbtr_iban,
                "creditor_iban": cdtr_iban
            }
            
        except Exception as e:
            logger.error(f"Failed to parse pacs.008 message: {e}")
            raise SwiftMessageError(f"pacs.008 parsing failed: {e}")
    
    def _parse_pacs002(self, root: ET.Element, ns: Dict[str, str]) -> Dict[str, any]:
        """Parse pacs.002 (Payment Status Report) message"""
        try:
            msg_id = root.find('.//ns:MsgId', ns).text if root.find('.//ns:MsgId', ns) is not None else None
            orgnl_msg_id = root.find('.//ns:OrgnlMsgId', ns).text if root.find('.//ns:OrgnlMsgId', ns) is not None else None
            
            # Extract status
            status_elem = root.find('.//ns:TxSts', ns)
            status = status_elem.text if status_elem is not None else None
            
            return {
                "message_type": "pacs.002",
                "message_id": msg_id,
                "original_message_id": orgnl_msg_id,
                "status": status
            }
            
        except Exception as e:
            logger.error(f"Failed to parse pacs.002 message: {e}")
            raise SwiftMessageError(f"pacs.002 parsing failed: {e}")
    
    def _parse_pacs004(self, root: ET.Element, ns: Dict[str, str]) -> Dict[str, any]:
        """Parse pacs.004 (Payment Return) message"""
        try:
            msg_id = root.find('.//ns:MsgId', ns).text if root.find('.//ns:MsgId', ns) is not None else None
            orgnl_msg_id = root.find('.//ns:OrgnlMsgId', ns).text if root.find('.//ns:OrgnlMsgId', ns) is not None else None
            
            # Extract return reason
            rsn_elem = root.find('.//ns:Rsn/ns:Cd', ns)
            return_reason = rsn_elem.text if rsn_elem is not None else None
            
            return {
                "message_type": "pacs.004",
                "message_id": msg_id,
                "original_message_id": orgnl_msg_id,
                "return_reason": return_reason
            }
            
        except Exception as e:
            logger.error(f"Failed to parse pacs.004 message: {e}")
            raise SwiftMessageError(f"pacs.004 parsing failed: {e}")
    
    async def validate_certificates(self) -> Dict[str, bool]:
        """Validate SWIFT certificates and connectivity"""
        try:
            results = {
                "client_cert_valid": False,
                "private_key_valid": False,
                "ca_cert_valid": False,
                "connectivity": False
            }
            
            # Validate client certificate
            try:
                with open(self.config.cert_path, 'rb') as f:
                    cert_data = f.read()
                    cert = x509.load_pem_x509_certificate(cert_data)
                    results["client_cert_valid"] = True
                    logger.info(f"Client certificate valid until: {cert.not_valid_after}")
            except Exception as e:
                logger.error(f"Client certificate validation failed: {e}")
            
            # Validate private key
            try:
                with open(self.config.key_path, 'rb') as f:
                    key_data = f.read()
                    private_key = serialization.load_pem_private_key(key_data, password=None)
                    results["private_key_valid"] = True
                    logger.info("Private key validation successful")
            except Exception as e:
                logger.error(f"Private key validation failed: {e}")
            
            # Validate CA certificate
            try:
                with open(self.config.ca_cert_path, 'rb') as f:
                    ca_data = f.read()
                    ca_cert = x509.load_pem_x509_certificate(ca_data)
                    results["ca_cert_valid"] = True
                    logger.info(f"CA certificate valid until: {ca_cert.not_valid_after}")
            except Exception as e:
                logger.error(f"CA certificate validation failed: {e}")
            
            # Test connectivity
            try:
                await self._test_connection()
                results["connectivity"] = True
                logger.info("SWIFTNet connectivity test successful")
            except Exception as e:
                logger.error(f"Connectivity test failed: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"Certificate validation failed: {e}")
            return results

# Factory function for creating SWIFT connector
async def create_swift_connector() -> SwiftConnector:
    """Create SWIFT connector with configuration from settings"""
    settings = get_settings()
    
    config = SwiftConnectorConfig(
        bic=settings.swift.bic,
        cert_path=settings.swift.cert_path,
        key_path=settings.swift.key_path,
        ca_cert_path=settings.swift.ca_cert_path,
        swiftnet_endpoint=settings.swift.endpoint,
        dry_run=settings.swift.dry_run
    )
    
    return SwiftConnector(config)