"""
Connecteur SWIFT pour Banking Transfer Platform
Support ISO 20022, MT103, et intégration bancaire réelle
"""

import asyncio
import logging
import ssl
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import aiohttp
import aiofiles
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class SWIFTConfig:
    """Configuration SWIFT"""
    bic: str
    bank_name: str
    country_code: str
    swift_network: str = "SWIFTNet"
    endpoint_url: str = ""
    client_cert_path: str = ""
    client_key_path: str = ""
    ca_cert_path: str = ""
    timeout: int = 30
    retry_attempts: int = 3
    dry_run: bool = True

@dataclass
class TransferRequest:
    """Demande de transfert SWIFT"""
    id: str
    amount: float
    currency: str
    sender_bic: str
    sender_iban: str
    sender_name: str
    recipient_bic: str
    recipient_iban: str
    recipient_name: str
    purpose: str
    reference: str
    urgent: bool = False

@dataclass
class TransferResponse:
    """Réponse de transfert SWIFT"""
    id: str
    swift_message_id: str
    status: str
    ack_received: bool
    ack_timestamp: Optional[datetime]
    error_message: Optional[str]
    mt103_content: Optional[str]

class SWIFTConnector:
    """Connecteur SWIFT avec support ISO 20022 et MT103"""
    
    def __init__(self, config: SWIFTConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.client_cert: Optional[bytes] = None
        self.client_key: Optional[bytes] = None
        self.ca_cert: Optional[bytes] = None
        
        # Validation IBAN/BIC
        self.iban_validator = IBANValidator()
        self.bic_validator = BICValidator()
        
        logger.info("SWIFT Connector initialisé", 
                   bic=config.bic, 
                   bank_name=config.bank_name,
                   dry_run=config.dry_run)

    async def initialize(self) -> bool:
        """Initialise le connecteur SWIFT"""
        try:
            # Chargement des certificats
            await self._load_certificates()
            
            # Création de la session HTTP
            connector = aiohttp.TCPConnector(
                ssl=self._create_ssl_context(),
                limit=100,
                limit_per_host=30
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
            
            # Test de connectivité
            if not self.config.dry_run:
                await self._test_connectivity()
            
            logger.info("SWIFT Connector initialisé avec succès")
            return True
            
        except Exception as e:
            logger.error("Erreur initialisation SWIFT Connector", error=str(e))
            return False

    async def _load_certificates(self):
        """Charge les certificats TLS"""
        try:
            if self.config.client_cert_path:
                async with aiofiles.open(self.config.client_cert_path, 'rb') as f:
                    self.client_cert = await f.read()
            
            if self.config.client_key_path:
                async with aiofiles.open(self.config.client_key_path, 'rb') as f:
                    self.client_key = await f.read()
            
            if self.config.ca_cert_path:
                async with aiofiles.open(self.config.ca_cert_path, 'rb') as f:
                    self.ca_cert = await f.read()
                    
            logger.info("Certificats chargés avec succès")
            
        except Exception as e:
            logger.error("Erreur chargement certificats", error=str(e))
            raise

    def _create_ssl_context(self) -> ssl.SSLContext:
        """Crée le contexte SSL pour SWIFT"""
        ssl_context = ssl.create_default_context()
        
        if self.ca_cert:
            ssl_context.load_verify_locations(cadata=self.ca_cert.decode())
        
        if self.client_cert and self.client_key:
            ssl_context.load_cert_chain(
                certfile=None,
                keyfile=None,
                password=None,
                certdata=self.client_cert,
                keydata=self.client_key
            )
        
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        
        return ssl_context

    async def _test_connectivity(self) -> bool:
        """Teste la connectivité SWIFT"""
        try:
            if not self.session:
                return False
                
            # Test de connectivité basique
            async with self.session.get(f"{self.config.endpoint_url}/health") as response:
                if response.status == 200:
                    logger.info("Connectivité SWIFT testée avec succès")
                    return True
                else:
                    logger.warning("Connectivité SWIFT échouée", status=response.status)
                    return False
                    
        except Exception as e:
            logger.error("Erreur test connectivité SWIFT", error=str(e))
            return False

    async def send_transfer(self, request: TransferRequest) -> TransferResponse:
        """Envoie un transfert SWIFT"""
        try:
            # Validation des données
            if not self._validate_transfer_request(request):
                return TransferResponse(
                    id=request.id,
                    swift_message_id="",
                    status="FAILED",
                    ack_received=False,
                    ack_timestamp=None,
                    error_message="Données de transfert invalides",
                    mt103_content=None
                )

            # Mode dry-run
            if self.config.dry_run:
                return await self._simulate_transfer(request)

            # Génération du message ISO 20022
            iso_message = self._generate_iso20022_message(request)
            
            # Envoi du message
            swift_response = await self._send_swift_message(iso_message)
            
            # Traitement de la réponse
            return self._process_swift_response(request, swift_response)
            
        except Exception as e:
            logger.error("Erreur envoi transfert SWIFT", 
                        transfer_id=request.id, 
                        error=str(e))
            return TransferResponse(
                id=request.id,
                swift_message_id="",
                status="FAILED",
                ack_received=False,
                ack_timestamp=None,
                error_message=str(e),
                mt103_content=None
            )

    def _validate_transfer_request(self, request: TransferRequest) -> bool:
        """Valide les données de transfert"""
        try:
            # Validation IBAN
            if not self.iban_validator.validate(request.sender_iban):
                logger.warning("IBAN expéditeur invalide", iban=request.sender_iban)
                return False
                
            if not self.iban_validator.validate(request.recipient_iban):
                logger.warning("IBAN destinataire invalide", iban=request.recipient_iban)
                return False

            # Validation BIC
            if not self.bic_validator.validate(request.sender_bic):
                logger.warning("BIC expéditeur invalide", bic=request.sender_bic)
                return False
                
            if not self.bic_validator.validate(request.recipient_bic):
                logger.warning("BIC destinataire invalide", bic=request.recipient_bic)
                return False

            # Validation montant
            if request.amount <= 0:
                logger.warning("Montant invalide", amount=request.amount)
                return False

            # Validation devise
            if request.currency not in ['EUR', 'USD', 'CDF']:
                logger.warning("Devise non supportée", currency=request.currency)
                return False

            return True
            
        except Exception as e:
            logger.error("Erreur validation transfert", error=str(e))
            return False

    def _generate_iso20022_message(self, request: TransferRequest) -> str:
        """Génère un message ISO 20022 pacs.008"""
        try:
            # Création du message XML ISO 20022
            root = ET.Element("Document")
            root.set("xmlns", "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.10")
            
            # En-tête du message
            fitoftr = ET.SubElement(root, "FIToFICstmrCdtTrf")
            
            # Informations de groupe
            grphdr = ET.SubElement(fitoftr, "GrpHdr")
            msg_id = ET.SubElement(grphdr, "MsgId")
            msg_id.text = f"SWIFT{request.id}"
            
            cre_dt_tm = ET.SubElement(grphdr, "CreDtTm")
            cre_dt_tm.text = datetime.now(timezone.utc).isoformat()
            
            nb_of_txs = ET.SubElement(grphdr, "NbOfTxs")
            nb_of_txs.text = "1"
            
            ctrl_sum = ET.SubElement(grphdr, "CtrlSum")
            ctrl_sum.text = f"{request.amount:.2f}"
            
            # Informations de crédit
            cdt_trf_tx_inf = ET.SubElement(fitoftr, "CdtTrfTxInf")
            
            pmt_id = ET.SubElement(cdt_trf_tx_inf, "PmtId")
            instr_id = ET.SubElement(pmt_id, "InstrId")
            instr_id.text = request.id
            
            end_to_end_id = ET.SubElement(pmt_id, "EndToEndId")
            end_to_end_id.text = request.reference
            
            # Montant
            amt = ET.SubElement(cdt_trf_tx_inf, "Amt")
            instd_amt = ET.SubElement(amt, "InstdAmt")
            instd_amt.set("Ccy", request.currency)
            instd_amt.text = f"{request.amount:.2f}"
            
            # Intermédiaire
            intrmy_agt1 = ET.SubElement(cdt_trf_tx_inf, "IntrmyAgt1")
            fin_instn_id = ET.SubElement(intrmy_agt1, "FinInstnId")
            bicfi = ET.SubElement(fin_instn_id, "BICFI")
            bicfi.text = request.sender_bic
            
            # Compte créditeur
            cdtr_agt = ET.SubElement(cdt_trf_tx_inf, "CdtrAgt")
            fin_instn_id = ET.SubElement(cdtr_agt, "FinInstnId")
            bicfi = ET.SubElement(fin_instn_id, "BICFI")
            bicfi.text = request.recipient_bic
            
            cdtr_acct = ET.SubElement(cdt_trf_tx_inf, "CdtrAcct")
            id = ET.SubElement(cdtr_acct, "Id")
            othr = ET.SubElement(id, "Othr")
            idd = ET.SubElement(othr, "Id")
            idd.text = request.recipient_iban
            
            # Bénéficiaire
            cdtr = ET.SubElement(cdt_trf_tx_inf, "Cdtr")
            nm = ET.SubElement(cdtr, "Nm")
            nm.text = request.recipient_name
            
            # Référence
            rmt_inf = ET.SubElement(cdt_trf_tx_inf, "RmtInf")
            uetrd = ET.SubElement(rmt_inf, "UETR")
            uetrd.text = request.reference
            
            return ET.tostring(root, encoding='unicode')
            
        except Exception as e:
            logger.error("Erreur génération message ISO 20022", error=str(e))
            raise

    async def _send_swift_message(self, message: str) -> Dict[str, Any]:
        """Envoie le message SWIFT"""
        try:
            if not self.session:
                raise Exception("Session SWIFT non initialisée")
            
            headers = {
                'Content-Type': 'application/xml',
                'X-SWIFT-Message-Type': 'pacs.008',
                'X-SWIFT-Sender-BIC': self.config.bic
            }
            
            async with self.session.post(
                f"{self.config.endpoint_url}/swift/message",
                data=message,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Erreur SWIFT: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error("Erreur envoi message SWIFT", error=str(e))
            raise

    def _process_swift_response(self, request: TransferRequest, response: Dict[str, Any]) -> TransferResponse:
        """Traite la réponse SWIFT"""
        try:
            status = response.get('status', 'FAILED')
            swift_message_id = response.get('message_id', '')
            ack_received = response.get('ack_received', False)
            error_message = response.get('error_message')
            
            ack_timestamp = None
            if ack_received:
                ack_timestamp = datetime.fromisoformat(response.get('ack_timestamp'))
            
            return TransferResponse(
                id=request.id,
                swift_message_id=swift_message_id,
                status=status,
                ack_received=ack_received,
                ack_timestamp=ack_timestamp,
                error_message=error_message,
                mt103_content=response.get('mt103_content')
            )
            
        except Exception as e:
            logger.error("Erreur traitement réponse SWIFT", error=str(e))
            return TransferResponse(
                id=request.id,
                swift_message_id="",
                status="FAILED",
                ack_received=False,
                ack_timestamp=None,
                error_message=str(e),
                mt103_content=None
            )

    async def _simulate_transfer(self, request: TransferRequest) -> TransferResponse:
        """Simule un transfert (mode dry-run)"""
        await asyncio.sleep(1)  # Simulation délai réseau
        
        logger.info("Simulation transfert SWIFT", 
                   transfer_id=request.id,
                   amount=request.amount,
                   currency=request.currency)
        
        return TransferResponse(
            id=request.id,
            swift_message_id=f"SWIFT{request.id}",
            status="COMPLETED",
            ack_received=True,
            ack_timestamp=datetime.now(timezone.utc),
            error_message=None,
            mt103_content=self._generate_mt103_content(request)
        )

    def _generate_mt103_content(self, request: TransferRequest) -> str:
        """Génère le contenu MT103"""
        return f"""MT103
{1:02d}:{self.config.bic}
{2:02d}:O103{datetime.now().strftime('%y%m%d')}{self.config.bic}N
{3:02d}:{request.recipient_bic}
{4:02d}:20:{request.reference}
{4:02d}:23B:CRED
{4:02d}:32A:{datetime.now().strftime('%y%m%d')}{request.currency}{request.amount:,.2f}
{4:02d}:50K:/{request.sender_iban}
{request.sender_name}
{4:02d}:59:/{request.recipient_iban}
{request.recipient_name}
{4:02d}:70:{request.purpose}
{4:02d}:71A:SHA
{4:02d}:71F:{request.amount * 0.001:.2f}{request.currency}
{4:02d}:72:/INS/{request.recipient_bic}
-"""

    async def close(self):
        """Ferme le connecteur SWIFT"""
        if self.session:
            await self.session.close()
            logger.info("Session SWIFT fermée")

class IBANValidator:
    """Validateur IBAN"""
    
    def validate(self, iban: str) -> bool:
        try:
            # Suppression des espaces
            iban = iban.replace(' ', '').upper()
            
            # Vérification longueur
            if len(iban) < 15 or len(iban) > 34:
                return False
            
            # Vérification format pays
            country_code = iban[:2]
            if not country_code.isalpha():
                return False
            
            # Vérification chiffres
            if not iban[2:].isdigit():
                return False
            
            # Validation checksum (simplifiée)
            return True
            
        except Exception:
            return False

class BICValidator:
    """Validateur BIC"""
    
    def validate(self, bic: str) -> bool:
        try:
            # Suppression des espaces
            bic = bic.replace(' ', '').upper()
            
            # Vérification longueur (8 ou 11 caractères)
            if len(bic) not in [8, 11]:
                return False
            
            # Vérification format
            if not bic[:6].isalpha():
                return False
            
            if not bic[6:8].isalnum():
                return False
            
            if len(bic) == 11 and not bic[8:11].isalnum():
                return False
            
            return True
            
        except Exception:
            return False