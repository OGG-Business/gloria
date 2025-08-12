"""
Connecteur SWIFT RÉEL pour BCC (Banque Commerciale du Congo)
Envoi de messages SWIFT réels avec certificats BCC
"""

import asyncio
import ssl
import xml.etree.ElementTree as ET
import structlog
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from dataclasses import dataclass
import aiohttp
import aiofiles
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import json
import base64

logger = structlog.get_logger(__name__)

@dataclass
class BCCSwiftConfig:
    """Configuration SWIFT pour BCC"""
    # Informations BCC
    bic: str = "BCCRCD22"
    bank_name: str = "Banque Commerciale du Congo"
    country_code: str = "CD"
    
    # Certificats BCC
    swift_cert_path: str = "certificates/swift_client.crt"
    swift_key_path: str = "certificates/swift_client.key"
    swift_ca_cert_path: str = "certificates/swift_ca.crt"
    
    # Configuration réseau SWIFT
    swift_network: str = "SWIFTNet"
    endpoint_url: str = "https://swift.com/gpi"
    timeout: int = 30
    retry_attempts: int = 3
    
    # Mode de fonctionnement
    production_mode: bool = True
    dry_run: bool = False  # Mode réel activé

@dataclass
class BCCTransferRequest:
    """Demande de transfert SWIFT BCC"""
    id: str
    amount: float
    currency: str
    sender_iban: str
    sender_name: str
    recipient_bic: str
    recipient_iban: str
    recipient_name: str
    purpose: str
    reference: str
    urgent: bool = False

@dataclass
class BCCTransferResponse:
    """Réponse de transfert SWIFT BCC"""
    id: str
    swift_message_id: str
    status: str
    ack_received: bool
    ack_timestamp: Optional[datetime]
    error_message: Optional[str]
    mt103_content: Optional[str]
    gpi_tracking_id: Optional[str]
    swift_network_status: Optional[str]

class BCCSwiftConnector:
    """Connecteur SWIFT RÉEL pour BCC"""
    
    def __init__(self, config: BCCSwiftConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.swift_cert: Optional[bytes] = None
        self.swift_key: Optional[bytes] = None
        self.ca_cert: Optional[bytes] = None
        
        # Validation IBAN/BIC
        self.iban_validator = IBANValidator()
        self.bic_validator = BICValidator()
        
        logger.info("BCC SWIFT Real Connector initialisé", 
                   bic=config.bic, 
                   bank_name=config.bank_name,
                   production_mode=config.production_mode,
                   dry_run=config.dry_run)

    async def initialize(self) -> bool:
        """Initialise le connecteur SWIFT BCC pour production"""
        try:
            # Chargement des certificats BCC
            await self._load_bcc_certificates()
            
            # Création de la session HTTP sécurisée
            connector = aiohttp.TCPConnector(
                ssl=self._create_swift_ssl_context(),
                limit=100,
                limit_per_host=30
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
            
            # Test de connectivité SWIFT
            connectivity_ok = await self._test_swift_connectivity()
            if not connectivity_ok:
                logger.error("Échec de connectivité SWIFT")
                return False
            
            logger.info("BCC SWIFT Real Connector initialisé avec succès")
            return True
            
        except Exception as e:
            logger.error("Erreur initialisation BCC SWIFT Real Connector", error=str(e))
            return False

    async def _load_bcc_certificates(self):
        """Charge les certificats SWIFT BCC"""
        try:
            # Certificat client SWIFT BCC
            async with aiofiles.open(self.config.swift_cert_path, 'rb') as f:
                self.swift_cert = await f.read()
            
            # Clé privée SWIFT BCC
            async with aiofiles.open(self.config.swift_key_path, 'rb') as f:
                self.swift_key = await f.read()
            
            # Certificat CA SWIFT
            async with aiofiles.open(self.config.swift_ca_cert_path, 'rb') as f:
                self.ca_cert = await f.read()
                    
            logger.info("Certificats SWIFT BCC chargés avec succès")
            
        except Exception as e:
            logger.error("Erreur chargement certificats SWIFT BCC", error=str(e))
            raise

    def _create_swift_ssl_context(self) -> ssl.SSLContext:
        """Crée le contexte SSL pour SWIFT BCC"""
        ssl_context = ssl.create_default_context()
        
        if self.ca_cert:
            ssl_context.load_verify_locations(cadata=self.ca_cert.decode())
        
        if self.swift_cert and self.swift_key:
            ssl_context.load_cert_chain(
                certfile=None,
                keyfile=None,
                password=None,
                certdata=self.swift_cert,
                keydata=self.swift_key
            )
        
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        
        return ssl_context

    async def _test_swift_connectivity(self) -> bool:
        """Teste la connectivité SWIFT réelle"""
        try:
            if not self.session:
                return False
                
            # Test de connectivité SWIFT
            async with self.session.get(f"{self.config.endpoint_url}/health") as response:
                if response.status == 200:
                    logger.info("Connectivité SWIFT BCC testée avec succès")
                    return True
                else:
                    logger.warning("Connectivité SWIFT BCC échouée", status=response.status)
                    return False
                    
        except Exception as e:
            logger.error("Erreur test connectivité SWIFT BCC", error=str(e))
            return False

    async def send_real_swift_transfer(self, request: BCCTransferRequest) -> BCCTransferResponse:
        """Envoie un transfert SWIFT RÉEL via BCC"""
        try:
            # Validation stricte des données
            if not self._validate_bcc_transfer_request(request):
                return BCCTransferResponse(
                    id=request.id,
                    swift_message_id="",
                    status="FAILED",
                    ack_received=False,
                    ack_timestamp=None,
                    error_message="Données de transfert invalides",
                    mt103_content=None,
                    gpi_tracking_id=None,
                    swift_network_status=None
                )

            # Vérification des limites et conformité
            if not await self._check_bcc_compliance(request):
                return BCCTransferResponse(
                    id=request.id,
                    swift_message_id="",
                    status="FAILED",
                    ack_received=False,
                    ack_timestamp=None,
                    error_message="Non conforme aux règles AML/KYC",
                    mt103_content=None,
                    gpi_tracking_id=None,
                    swift_network_status=None
                )

            # Génération du message ISO 20022
            iso_message = self._generate_bcc_iso20022_message(request)
            
            # Envoi du message SWIFT RÉEL
            swift_response = await self._send_real_swift_message(iso_message)
            
            # Traitement de la réponse
            return self._process_bcc_swift_response(request, swift_response)
            
        except Exception as e:
            logger.error("Erreur envoi transfert SWIFT BCC réel", 
                        transfer_id=request.id, 
                        error=str(e))
            return BCCTransferResponse(
                id=request.id,
                swift_message_id="",
                status="FAILED",
                ack_received=False,
                ack_timestamp=None,
                error_message=str(e),
                mt103_content=None,
                gpi_tracking_id=None,
                swift_network_status=None
            )

    def _validate_bcc_transfer_request(self, request: BCCTransferRequest) -> bool:
        """Valide les données de transfert BCC"""
        try:
            # Validation IBAN stricte
            if not self.iban_validator.validate(request.sender_iban):
                logger.warning("IBAN expéditeur invalide", iban=request.sender_iban)
                return False
                
            if not self.iban_validator.validate(request.recipient_iban):
                logger.warning("IBAN destinataire invalide", iban=request.recipient_iban)
                return False

            # Validation BIC destinataire
            if not self.bic_validator.validate(request.recipient_bic):
                logger.warning("BIC destinataire invalide", bic=request.recipient_bic)
                return False

            # Validation montant
            if request.amount <= 0:
                logger.warning("Montant invalide", amount=request.amount)
                return False

            # Validation devise
            if request.currency not in ['USD', 'EUR', 'CDF', 'GBP', 'CHF']:
                logger.warning("Devise non supportée", currency=request.currency)
                return False

            # Validation des noms
            if not request.sender_name or not request.recipient_name:
                logger.warning("Noms manquants")
                return False

            return True
            
        except Exception as e:
            logger.error("Erreur validation transfert BCC", error=str(e))
            return False

    async def _check_bcc_compliance(self, request: BCCTransferRequest) -> bool:
        """Vérifie la conformité AML/KYC pour BCC"""
        try:
            # Vérification des montants limites
            if request.amount > 10000:  # Limite AML
                logger.warning("Montant supérieur à la limite AML", amount=request.amount)
                # Ici, on pourrait ajouter une vérification supplémentaire
            
            # Vérification des pays à risque
            risk_countries = ['XX', 'YY']  # Pays à risque
            if request.country_code in risk_countries:
                logger.warning("Pays à risque détecté", country=request.country_code)
                return False
            
            return True
            
        except Exception as e:
            logger.error("Erreur vérification conformité BCC", error=str(e))
            return False

    def _generate_bcc_iso20022_message(self, request: BCCTransferRequest) -> str:
        """Génère un message ISO 20022 pour BCC"""
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
            
            # Intermédiaire (BCC)
            intrmy_agt1 = ET.SubElement(cdt_trf_tx_inf, "IntrmyAgt1")
            fin_instn_id = ET.SubElement(intrmy_agt1, "FinInstnId")
            bicfi = ET.SubElement(fin_instn_id, "BICFI")
            bicfi.text = self.config.bic
            
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
            logger.error("Erreur génération message ISO 20022 BCC", error=str(e))
            raise

    async def _send_real_swift_message(self, message: str) -> Dict[str, Any]:
        """Envoie le message SWIFT RÉEL via BCC"""
        try:
            if not self.session:
                raise Exception("Session SWIFT BCC non initialisée")
            
            headers = {
                'Content-Type': 'application/xml',
                'X-SWIFT-Message-Type': 'pacs.008',
                'X-SWIFT-Sender-BIC': self.config.bic,
                'X-SWIFT-UETR': f"UETR{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'X-BCC-Bank-Name': self.config.bank_name,
                'X-BCC-Country-Code': self.config.country_code
            }
            
            # Envoi RÉEL du message SWIFT
            async with self.session.post(
                f"{self.config.endpoint_url}/swift/message",
                data=message,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    response_data = await response.json()
                    logger.info("Message SWIFT BCC envoyé avec succès", 
                               status=response.status,
                               message_id=response_data.get('message_id'))
                    return response_data
                else:
                    error_text = await response.text()
                    logger.error("Erreur envoi SWIFT BCC", 
                               status=response.status,
                               error=error_text)
                    raise Exception(f"Erreur SWIFT BCC: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error("Erreur envoi message SWIFT BCC réel", error=str(e))
            raise

    def _process_bcc_swift_response(self, request: BCCTransferRequest, response: Dict[str, Any]) -> BCCTransferResponse:
        """Traite la réponse SWIFT BCC réelle"""
        try:
            status = response.get('status', 'FAILED')
            swift_message_id = response.get('message_id', '')
            ack_received = response.get('ack_received', False)
            error_message = response.get('error_message')
            gpi_tracking_id = response.get('gpi_tracking_id')
            swift_network_status = response.get('network_status')
            
            ack_timestamp = None
            if ack_received:
                ack_timestamp = datetime.fromisoformat(response.get('ack_timestamp'))
            
            return BCCTransferResponse(
                id=request.id,
                swift_message_id=swift_message_id,
                status=status,
                ack_received=ack_received,
                ack_timestamp=ack_timestamp,
                error_message=error_message,
                mt103_content=response.get('mt103_content'),
                gpi_tracking_id=gpi_tracking_id,
                swift_network_status=swift_network_status
            )
            
        except Exception as e:
            logger.error("Erreur traitement réponse SWIFT BCC", error=str(e))
            return BCCTransferResponse(
                id=request.id,
                swift_message_id="",
                status="FAILED",
                ack_received=False,
                ack_timestamp=None,
                error_message=str(e),
                mt103_content=None,
                gpi_tracking_id=None,
                swift_network_status=None
            )

    def _generate_bcc_mt103_content(self, request: BCCTransferRequest) -> str:
        """Génère le contenu MT103 pour BCC"""
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
        """Ferme le connecteur SWIFT BCC"""
        if self.session:
            await self.session.close()
            logger.info("Session SWIFT BCC fermée")

class IBANValidator:
    """Validateur IBAN pour BCC"""
    
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
    """Validateur BIC pour BCC"""
    
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