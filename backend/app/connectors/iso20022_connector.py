"""
ISO 20022 connector for Banking Transfer Platform
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import structlog

logger = structlog.get_logger()

class ISO20022Message:
    """ISO 20022 message model"""
    
    def __init__(self, message_id: str, message_type: str, content: str):
        self.message_id = message_id
        self.message_type = message_type
        self.content = content
        self.created_at = datetime.now(timezone.utc)

class ISO20022Connector:
    """ISO 20022 connector for XML messages"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.bic = config.get("bic", "TESTUS33XXX")
        self.dry_run = config.get("dry_run", True)
        
    def create_pacs008_message(self, transfer) -> ISO20022Message:
        """Create pacs.008 message for transfer"""
        try:
            message_id = f"pacs008_{datetime.now().strftime('%Y%m%d%H%M%S')}_{str(uuid.uuid4())[:8]}"
            
            # Create simplified pacs.008 XML content
            content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>{message_id}</MsgId>
      <CreDtTm>{datetime.now(timezone.utc).isoformat()}</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <TtlIntrBkSttlmAmt Ccy="{transfer.currency}">{transfer.amount:.2f}</TtlIntrBkSttlmAmt>
      <IntrBkSttlmDt>{datetime.now().strftime('%Y-%m-%d')}</IntrBkSttlmDt>
      <SttlmInf>
        <SttlmMtd>CLRG</SttlmMtd>
      </SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <InstrId>{transfer.transfer_id}</InstrId>
        <EndToEndId>{transfer.transfer_id}</EndToEndId>
        <TxId>{transfer.transfer_id}</TxId>
      </PmtId>
      <IntrBkSttlmAmt Ccy="{transfer.currency}">{transfer.amount:.2f}</IntrBkSttlmAmt>
      <IntrBkSttlmDt>{datetime.now().strftime('%Y-%m-%d')}</IntrBkSttlmDt>
      <SttlmTmIndctn>
        <DbtDtTm>{datetime.now(timezone.utc).isoformat()}</DbtDtTm>
      </SttlmTmIndctn>
      <InstgAgt>
        <FinInstnId>
          <BICFI>{self.bic}</BICFI>
        </FinInstnId>
      </InstgAgt>
      <InstdAgt>
        <FinInstnId>
          <BICFI>{transfer.beneficiary_bic or 'BENEBICXXXXX'}</BICFI>
        </FinInstnId>
      </InstdAgt>
      <Dbtr>
        <Nm>{transfer.source_account.holder_name}</Nm>
        <PstlAdr>
          <Ctry>US</Ctry>
        </PstlAdr>
        <Id>
          <OrgId>
            <Othr>
              <Id>{transfer.source_account.iban}</Id>
            </Othr>
          </OrgId>
        </Id>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <IBAN>{transfer.source_account.iban}</IBAN>
        </Id>
      </DbtrAcct>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>{self.bic}</BICFI>
        </FinInstnId>
      </DbtrAgt>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>{transfer.beneficiary_bic or 'BENEBICXXXXX'}</BICFI>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>{transfer.beneficiary_name}</Nm>
        <PstlAdr>
          <Ctry>US</Ctry>
        </PstlAdr>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <IBAN>{transfer.beneficiary_iban}</IBAN>
        </Id>
      </CdtrAcct>
      <Purp>
        <Cd>SUPP</Cd>
      </Purp>
      <RgltryRptg>
        <DbtCdtRptgInd>CRED</DbtCdtRptgInd>
        <Authrty>
          <Nm>Central Bank</Nm>
        </Authrty>
        <Dtls>
          <Tp>CRED</Tp>
          <Dt>2023-12-01</Dt>
          <Ctry>US</Ctry>
          <Cd>CRED</Cd>
          <Amt Ccy="{transfer.currency}">{transfer.amount:.2f}</Amt>
        </Dtls>
      </RgltryRptg>
      <RmtInf>
        <UETR>{str(uuid.uuid4())}</UETR>
        <Strd>
          <RfrdDocInf>
            <Tp>
              <CdOrPrtry>
                <Cd>CINV</Cd>
              </CdOrPrtry>
            </Tp>
            <Nb>{transfer.transfer_id}</Nb>
          </RfrdDocInf>
          <RfrdDocAmt>
            <RmtdAmt Ccy="{transfer.currency}">{transfer.amount:.2f}</RmtdAmt>
          </RfrdDocAmt>
        </Strd>
      </RmtInf>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>"""
            
            message = ISO20022Message(message_id, "pacs.008", content)
            logger.info(f"Created pacs.008 message: {message_id}")
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to create pacs.008 message: {e}")
            raise
    
    def parse_pacs008_message(self, content: str) -> Dict[str, Any]:
        """Parse pacs.008 message content"""
        try:
            # Simplified parsing - in production use proper XML parsing
            logger.info("Parsing pacs.008 message")
            
            # Mock parsed data
            parsed_data = {
                "message_id": "parsed_message_id",
                "transfer_amount": 1000.00,
                "currency": "USD",
                "debtor_iban": "US123456789",
                "creditor_iban": "US987654321",
                "debtor_name": "John Doe",
                "creditor_name": "Jane Smith",
                "transfer_id": "TRF123456"
            }
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Failed to parse pacs.008 message: {e}")
            raise

def create_iso20022_connector() -> ISO20022Connector:
    """Create ISO 20022 connector instance"""
    config = {
        "bic": "TESTUS33XXX",
        "dry_run": True
    }
    
    return ISO20022Connector(config)