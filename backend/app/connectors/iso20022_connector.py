"""
ISO 20022 Connector for Banking Transfer Platform
Handles XML message parsing, validation, and serialization
"""

import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import xmltodict
from pydantic import BaseModel, Field, validator
import aiofiles

logger = logging.getLogger(__name__)

@dataclass
class ISO20022Message:
    """ISO 20022 message structure"""
    message_type: str  # pacs.008, pacs.002, pacs.004, etc.
    message_id: str
    creation_datetime: datetime
    content: str
    sender_bic: str
    receiver_bic: str
    status: str = "PENDING"

class ISO20022ConnectorConfig(BaseModel):
    """ISO 20022 connector configuration"""
    namespace_map: Dict[str, str] = Field(default={
        "pacs": "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08",
        "pacs002": "urn:iso:std:iso:20022:tech:xsd:pacs.002.001.10",
        "pacs004": "urn:iso:std:iso:20022:tech:xsd:pacs.004.001.09",
        "head": "urn:iso:std:iso:20022:tech:xsd:head.001.001.01"
    })
    schema_validation: bool = Field(True, description="Enable XML schema validation")
    dry_run: bool = Field(True, description="Dry run mode for testing")
    timeout: int = Field(30, description="Processing timeout in seconds")

class ISO20022Connector:
    """ISO 20022 connector for XML message handling"""
    
    def __init__(self, config: ISO20022ConnectorConfig):
        self.config = config
        self.namespace_map = config.namespace_map
        
    def create_pacs008_message(self, transfer) -> ISO20022Message:
        """Create pacs.008 (Customer Credit Transfer) message"""
        try:
            message_id = f"MSG_{transfer.transfer_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            creation_datetime = datetime.now(timezone.utc)
            
            # Create XML content
            xml_content = self._build_pacs008_xml(transfer, message_id, creation_datetime)
            
            return ISO20022Message(
                message_type="pacs.008",
                message_id=message_id,
                creation_datetime=creation_datetime,
                content=xml_content,
                sender_bic=transfer.source_account.bic,
                receiver_bic=transfer.destination_account.bic
            )
            
        except Exception as e:
            logger.error(f"Failed to create pacs.008 message: {e}")
            raise Exception(f"pacs.008 creation failed: {e}")
    
    def _build_pacs008_xml(self, transfer, message_id: str, creation_datetime: datetime) -> str:
        """Build pacs.008 XML content"""
        try:
            # Create root element
            root = ET.Element("Document", {
                "xmlns": self.namespace_map["pacs"],
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"
            })
            
            # Create FIToFICstmrCdtTrf element
            fitoficstmrcdttrf = ET.SubElement(root, "FIToFICstmrCdtTrf")
            
            # Create GrpHdr (Group Header)
            grphdr = ET.SubElement(fitoficstmrcdttrf, "GrpHdr")
            ET.SubElement(grphdr, "MsgId").text = message_id
            ET.SubElement(grphdr, "CreDtTm").text = creation_datetime.isoformat()
            ET.SubElement(grphdr, "NbOfTxs").text = "1"
            ET.SubElement(grphdr, "CtrlSum").text = f"{transfer.amount:.2f}"
            
            # Create InitgPty (Initiating Party)
            initgpty = ET.SubElement(grphdr, "InitgPty")
            initgpty_id = ET.SubElement(initgpty, "Id")
            initgpty_org = ET.SubElement(initgpty_id, "OrgId")
            ET.SubElement(initgpty_org, "BICFI").text = transfer.source_account.bic
            
            # Create CdtTrfTxInf (Credit Transfer Transaction Information)
            cdttrftxinf = ET.SubElement(fitoficstmrcdttrf, "CdtTrfTxInf")
            
            # Create PmtId (Payment Identification)
            pmtid = ET.SubElement(cdttrftxinf, "PmtId")
            ET.SubElement(pmtid, "InstrId").text = transfer.transfer_id
            ET.SubElement(pmtid, "EndToEndId").text = transfer.transfer_id
            
            # Create IntrBkSttlmAmt (Interbank Settlement Amount)
            intrbksttlmamt = ET.SubElement(cdttrftxinf, "IntrBkSttlmAmt")
            intrbksttlmamt.set("Ccy", transfer.currency)
            intrbksttlmamt.text = f"{transfer.amount:.2f}"
            
            # Create ChrgBr (Charge Bearer)
            ET.SubElement(cdttrftxinf, "ChrgBr").text = "SHAR"
            
            # Create CdtrAgt (Creditor Agent)
            cdtr_agt = ET.SubElement(cdttrftxinf, "CdtrAgt")
            cdtr_agt_fin_instn = ET.SubElement(cdtr_agt, "FinInstnId")
            ET.SubElement(cdtr_agt_fin_instn, "BICFI").text = transfer.destination_account.bic
            
            # Create Cdtr (Creditor)
            cdtr = ET.SubElement(cdttrftxinf, "Cdtr")
            ET.SubElement(cdtr, "Nm").text = transfer.beneficiary_name
            
            # Create CdtrAcct (Creditor Account)
            cdtr_acct = ET.SubElement(cdttrftxinf, "CdtrAcct")
            cdtr_acct_id = ET.SubElement(cdtr_acct, "Id")
            cdtr_acct_othr = ET.SubElement(cdtr_acct_id, "Othr")
            ET.SubElement(cdtr_acct_othr, "Id").text = transfer.destination_account.iban
            
            # Create Purp (Purpose)
            purp = ET.SubElement(cdttrftxinf, "Purp")
            ET.SubElement(purp, "Cd").text = "CASH"
            
            # Convert to string
            xml_string = ET.tostring(root, encoding='unicode', method='xml')
            
            # Add XML declaration
            xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
            return xml_declaration + xml_string
            
        except Exception as e:
            logger.error(f"Failed to build pacs.008 XML: {e}")
            raise Exception(f"XML building failed: {e}")
    
    def parse_message(self, xml_content: str) -> Dict[str, Any]:
        """Parse ISO 20022 XML message"""
        try:
            # Parse XML
            root = ET.fromstring(xml_content)
            
            # Determine message type
            message_type = self._get_message_type(root)
            
            # Parse based on message type
            if message_type == "pacs.008":
                return self._parse_pacs008(root)
            elif message_type == "pacs.002":
                return self._parse_pacs002(root)
            elif message_type == "pacs.004":
                return self._parse_pacs004(root)
            else:
                raise Exception(f"Unsupported message type: {message_type}")
                
        except Exception as e:
            logger.error(f"Failed to parse ISO 20022 message: {e}")
            raise Exception(f"Message parsing failed: {e}")
    
    def _get_message_type(self, root: ET.Element) -> str:
        """Determine ISO 20022 message type from root element"""
        tag = root.tag
        if "pacs.008" in tag:
            return "pacs.008"
        elif "pacs.002" in tag:
            return "pacs.002"
        elif "pacs.004" in tag:
            return "pacs.004"
        else:
            return "unknown"
    
    def _parse_pacs008(self, root: ET.Element) -> Dict[str, Any]:
        """Parse pacs.008 message"""
        try:
            # Extract basic information
            msg_id = root.find(".//MsgId")
            msg_id_text = msg_id.text if msg_id is not None else None
            
            cre_dt_tm = root.find(".//CreDtTm")
            cre_dt_tm_text = cre_dt_tm.text if cre_dt_tm is not None else None
            
            # Extract transfer information
            instr_id = root.find(".//InstrId")
            instr_id_text = instr_id.text if instr_id is not None else None
            
            end_to_end_id = root.find(".//EndToEndId")
            end_to_end_id_text = end_to_end_id.text if end_to_end_id is not None else None
            
            # Extract amount and currency
            amount_elem = root.find(".//IntrBkSttlmAmt")
            amount = float(amount_elem.text) if amount_elem is not None else None
            currency = amount_elem.get('Ccy') if amount_elem is not None else None
            
            return {
                "message_type": "pacs.008",
                "message_id": msg_id_text,
                "creation_datetime": cre_dt_tm_text,
                "instruction_id": instr_id_text,
                "end_to_end_id": end_to_end_id_text,
                "amount": amount,
                "currency": currency
            }
            
        except Exception as e:
            logger.error(f"Failed to parse pacs.008 message: {e}")
            raise Exception(f"pacs.008 parsing failed: {e}")
    
    def _parse_pacs002(self, root: ET.Element) -> Dict[str, Any]:
        """Parse pacs.002 message"""
        try:
            msg_id = root.find(".//MsgId")
            msg_id_text = msg_id.text if msg_id is not None else None
            
            orgnl_msg_id = root.find(".//OrgnlMsgId")
            orgnl_msg_id_text = orgnl_msg_id.text if orgnl_msg_id is not None else None
            
            # Extract status
            status_elem = root.find(".//TxSts")
            status = status_elem.text if status_elem is not None else None
            
            return {
                "message_type": "pacs.002",
                "message_id": msg_id_text,
                "original_message_id": orgnl_msg_id_text,
                "status": status
            }
            
        except Exception as e:
            logger.error(f"Failed to parse pacs.002 message: {e}")
            raise Exception(f"pacs.002 parsing failed: {e}")
    
    def _parse_pacs004(self, root: ET.Element) -> Dict[str, Any]:
        """Parse pacs.004 message"""
        try:
            msg_id = root.find(".//MsgId")
            msg_id_text = msg_id.text if msg_id is not None else None
            
            orgnl_msg_id = root.find(".//OrgnlMsgId")
            orgnl_msg_id_text = orgnl_msg_id.text if orgnl_msg_id is not None else None
            
            # Extract return reason
            rsn_elem = root.find(".//Rsn/Cd")
            return_reason = rsn_elem.text if rsn_elem is not None else None
            
            return {
                "message_type": "pacs.004",
                "message_id": msg_id_text,
                "original_message_id": orgnl_msg_id_text,
                "return_reason": return_reason
            }
            
        except Exception as e:
            logger.error(f"Failed to parse pacs.004 message: {e}")
            raise Exception(f"pacs.004 parsing failed: {e}")
    
    def validate_xml_schema(self, xml_content: str) -> bool:
        """Validate XML against ISO 20022 schema"""
        if not self.config.schema_validation:
            return True
            
        try:
            # Parse XML to check basic structure
            root = ET.fromstring(xml_content)
            
            # Basic validation - check required elements
            message_type = self._get_message_type(root)
            
            if message_type == "pacs.008":
                required_elements = ["MsgId", "CreDtTm", "IntrBkSttlmAmt"]
            elif message_type == "pacs.002":
                required_elements = ["MsgId", "OrgnlMsgId", "TxSts"]
            elif message_type == "pacs.004":
                required_elements = ["MsgId", "OrgnlMsgId", "Rsn"]
            else:
                return False
            
            # Check if required elements exist
            for element in required_elements:
                if root.find(f".//{element}") is None:
                    logger.warning(f"Missing required element: {element}")
                    return False
            
            logger.info(f"XML schema validation passed for {message_type}")
            return True
            
        except Exception as e:
            logger.error(f"XML schema validation failed: {e}")
            return False

# Factory function for creating ISO 20022 connector
def create_iso20022_connector() -> ISO20022Connector:
    """Create ISO 20022 connector with configuration from settings"""
    config = ISO20022ConnectorConfig(
        schema_validation=True,
        dry_run=True
    )
    
    return ISO20022Connector(config)