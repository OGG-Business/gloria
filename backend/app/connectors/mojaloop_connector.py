"""
Connecteur Mojaloop pour Banking Transfer Platform
Support des corridors africains et intégration DFSP
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import aiohttp
import structlog
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

logger = structlog.get_logger(__name__)

@dataclass
class MojaloopConfig:
    """Configuration Mojaloop"""
    dfsp_id: str
    dfsp_name: str
    currency: str = "CDF"
    country_code: str = "CD"
    mojaloop_hub_url: str = "https://hub.mojaloop.io"
    scheme_adapter_url: str = ""
    client_private_key_path: str = ""
    client_cert_path: str = ""
    timeout: int = 30
    retry_attempts: int = 3
    dry_run: bool = True

@dataclass
class MojaloopTransferRequest:
    """Demande de transfert Mojaloop"""
    id: str
    amount: float
    currency: str
    payer_msisdn: str
    payer_name: str
    payee_msisdn: str
    payee_name: str
    purpose: str
    reference: str
    urgent: bool = False

@dataclass
class MojaloopTransferResponse:
    """Réponse de transfert Mojaloop"""
    id: str
    mojaloop_transaction_id: str
    status: str
    quote_id: str
    transfer_id: str
    settlement_completed: bool
    settlement_timestamp: Optional[datetime]
    error_message: Optional[str]

class MojaloopConnector:
    """Connecteur Mojaloop avec support DFSP et settlement"""
    
    def __init__(self, config: MojaloopConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.private_key: Optional[rsa.RSAPrivateKey] = None
        self.client_cert: Optional[bytes] = None
        
        # Validation MSISDN
        self.msisdn_validator = MSISDNValidator()
        
        logger.info("Mojaloop Connector initialisé", 
                   dfsp_id=config.dfsp_id,
                   dfsp_name=config.dfsp_name,
                   currency=config.currency,
                   dry_run=config.dry_run)

    async def initialize(self) -> bool:
        """Initialise le connecteur Mojaloop"""
        try:
            # Chargement des clés
            await self._load_keys()
            
            # Création de la session HTTP
            connector = aiohttp.TCPConnector(
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
            
            logger.info("Mojaloop Connector initialisé avec succès")
            return True
            
        except Exception as e:
            logger.error("Erreur initialisation Mojaloop Connector", error=str(e))
            return False

    async def _load_keys(self):
        """Charge les clés privées et certificats"""
        try:
            if self.config.client_private_key_path:
                # Chargement de la clé privée RSA
                with open(self.config.client_private_key_path, 'rb') as f:
                    private_key_data = f.read()
                    self.private_key = serialization.load_pem_private_key(
                        private_key_data,
                        password=None
                    )
            
            if self.config.client_cert_path:
                with open(self.config.client_cert_path, 'rb') as f:
                    self.client_cert = f.read()
                    
            logger.info("Clés Mojaloop chargées avec succès")
            
        except Exception as e:
            logger.error("Erreur chargement clés Mojaloop", error=str(e))
            raise

    async def _test_connectivity(self) -> bool:
        """Teste la connectivité Mojaloop"""
        try:
            if not self.session:
                return False
                
            # Test de connectivité au Hub Mojaloop
            async with self.session.get(f"{self.config.mojaloop_hub_url}/health") as response:
                if response.status == 200:
                    logger.info("Connectivité Mojaloop testée avec succès")
                    return True
                else:
                    logger.warning("Connectivité Mojaloop échouée", status=response.status)
                    return False
                    
        except Exception as e:
            logger.error("Erreur test connectivité Mojaloop", error=str(e))
            return False

    async def send_transfer(self, request: MojaloopTransferRequest) -> MojaloopTransferResponse:
        """Envoie un transfert Mojaloop"""
        try:
            # Validation des données
            if not self._validate_transfer_request(request):
                return MojaloopTransferResponse(
                    id=request.id,
                    mojaloop_transaction_id="",
                    status="FAILED",
                    quote_id="",
                    transfer_id="",
                    settlement_completed=False,
                    settlement_timestamp=None,
                    error_message="Données de transfert invalides"
                )

            # Mode dry-run
            if self.config.dry_run:
                return await self._simulate_transfer(request)

            # Processus Mojaloop complet
            # 1. Demande de quote
            quote_response = await self._request_quote(request)
            if not quote_response.get('success'):
                return MojaloopTransferResponse(
                    id=request.id,
                    mojaloop_transaction_id="",
                    status="FAILED",
                    quote_id="",
                    transfer_id="",
                    settlement_completed=False,
                    settlement_timestamp=None,
                    error_message=quote_response.get('error', 'Erreur quote')
                )

            quote_id = quote_response['quote_id']
            
            # 2. Demande de transfert
            transfer_response = await self._request_transfer(request, quote_id)
            if not transfer_response.get('success'):
                return MojaloopTransferResponse(
                    id=request.id,
                    mojaloop_transaction_id="",
                    status="FAILED",
                    quote_id=quote_id,
                    transfer_id="",
                    settlement_completed=False,
                    settlement_timestamp=None,
                    error_message=transfer_response.get('error', 'Erreur transfert')
                )

            transfer_id = transfer_response['transfer_id']
            
            # 3. Vérification du settlement
            settlement_response = await self._check_settlement(transfer_id)
            
            return MojaloopTransferResponse(
                id=request.id,
                mojaloop_transaction_id=transfer_id,
                status="COMPLETED" if settlement_response['completed'] else "PENDING",
                quote_id=quote_id,
                transfer_id=transfer_id,
                settlement_completed=settlement_response['completed'],
                settlement_timestamp=settlement_response.get('timestamp'),
                error_message=None
            )
            
        except Exception as e:
            logger.error("Erreur envoi transfert Mojaloop", 
                        transfer_id=request.id, 
                        error=str(e))
            return MojaloopTransferResponse(
                id=request.id,
                mojaloop_transaction_id="",
                status="FAILED",
                quote_id="",
                transfer_id="",
                settlement_completed=False,
                settlement_timestamp=None,
                error_message=str(e)
            )

    def _validate_transfer_request(self, request: MojaloopTransferRequest) -> bool:
        """Valide les données de transfert Mojaloop"""
        try:
            # Validation MSISDN
            if not self.msisdn_validator.validate(request.payer_msisdn):
                logger.warning("MSISDN payeur invalide", msisdn=request.payer_msisdn)
                return False
                
            if not self.msisdn_validator.validate(request.payee_msisdn):
                logger.warning("MSISDN bénéficiaire invalide", msisdn=request.payee_msisdn)
                return False

            # Validation montant
            if request.amount <= 0:
                logger.warning("Montant invalide", amount=request.amount)
                return False

            # Validation devise
            if request.currency != self.config.currency:
                logger.warning("Devise non supportée", currency=request.currency)
                return False

            # Validation noms
            if not request.payer_name or not request.payee_name:
                logger.warning("Noms manquants")
                return False

            return True
            
        except Exception as e:
            logger.error("Erreur validation transfert Mojaloop", error=str(e))
            return False

    async def _request_quote(self, request: MojaloopTransferRequest) -> Dict[str, Any]:
        """Demande une quote Mojaloop"""
        try:
            quote_id = str(uuid.uuid4())
            
            quote_data = {
                "quoteId": quote_id,
                "transactionId": request.id,
                "transactionRequestId": request.id,
                "payer": {
                    "partyIdType": "MSISDN",
                    "partyIdentifier": request.payer_msisdn,
                    "fspId": self.config.dfsp_id
                },
                "payee": {
                    "partyIdType": "MSISDN",
                    "partyIdentifier": request.payee_msisdn
                },
                "amountType": "SEND",
                "amount": {
                    "currency": request.currency,
                    "amount": str(request.amount)
                },
                "transactionType": {
                    "scenario": "TRANSFER",
                    "subScenario": "TRANSFER",
                    "initiator": "PAYER",
                    "initiatorType": "CONSUMER"
                },
                "note": request.purpose
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Date': datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'),
                'X-Request-ID': quote_id,
                'X-DFSP-ID': self.config.dfsp_id
            }
            
            if self.private_key:
                # Signature de la requête
                signature = self._sign_request(quote_data, headers)
                headers['Authorization'] = f'Signature {signature}'
            
            async with self.session.post(
                f"{self.config.mojaloop_hub_url}/quotes",
                json=quote_data,
                headers=headers
            ) as response:
                
                if response.status == 202:
                    return {
                        'success': True,
                        'quote_id': quote_id
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f"Erreur quote: {response.status} - {error_text}"
                    }
                    
        except Exception as e:
            logger.error("Erreur demande quote Mojaloop", error=str(e))
            return {
                'success': False,
                'error': str(e)
            }

    async def _request_transfer(self, request: MojaloopTransferRequest, quote_id: str) -> Dict[str, Any]:
        """Demande un transfert Mojaloop"""
        try:
            transfer_id = str(uuid.uuid4())
            
            transfer_data = {
                "transferId": transfer_id,
                "quoteId": quote_id,
                "payerFsp": self.config.dfsp_id,
                "payeeFsp": "payee-dfsp",
                "amount": {
                    "currency": request.currency,
                    "amount": str(request.amount)
                },
                "ilpPacket": self._generate_ilp_packet(request),
                "condition": self._generate_fulfillment_condition(),
                "expiration": (datetime.now(timezone.utc).timestamp() + 300) * 1000,  # 5 minutes
                "extensionList": [
                    {
                        "key": "purpose",
                        "value": request.purpose
                    },
                    {
                        "key": "reference",
                        "value": request.reference
                    }
                ]
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Date': datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'),
                'X-Request-ID': transfer_id,
                'X-DFSP-ID': self.config.dfsp_id
            }
            
            if self.private_key:
                # Signature de la requête
                signature = self._sign_request(transfer_data, headers)
                headers['Authorization'] = f'Signature {signature}'
            
            async with self.session.post(
                f"{self.config.mojaloop_hub_url}/transfers",
                json=transfer_data,
                headers=headers
            ) as response:
                
                if response.status == 202:
                    return {
                        'success': True,
                        'transfer_id': transfer_id
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f"Erreur transfert: {response.status} - {error_text}"
                    }
                    
        except Exception as e:
            logger.error("Erreur demande transfert Mojaloop", error=str(e))
            return {
                'success': False,
                'error': str(e)
            }

    async def _check_settlement(self, transfer_id: str) -> Dict[str, Any]:
        """Vérifie le settlement d'un transfert"""
        try:
            headers = {
                'X-Request-ID': str(uuid.uuid4()),
                'X-DFSP-ID': self.config.dfsp_id
            }
            
            async with self.session.get(
                f"{self.config.mojaloop_hub_url}/transfers/{transfer_id}",
                headers=headers
            ) as response:
                
                if response.status == 200:
                    transfer_data = await response.json()
                    completed = transfer_data.get('transferState') == 'COMMITTED'
                    
                    return {
                        'completed': completed,
                        'timestamp': datetime.now(timezone.utc) if completed else None
                    }
                else:
                    return {
                        'completed': False,
                        'timestamp': None
                    }
                    
        except Exception as e:
            logger.error("Erreur vérification settlement", error=str(e))
            return {
                'completed': False,
                'timestamp': None
            }

    def _generate_ilp_packet(self, request: MojaloopTransferRequest) -> str:
        """Génère un packet ILP pour Mojaloop"""
        # Packet ILP simplifié
        ilp_data = {
            "amount": str(request.amount),
            "account": request.payee_msisdn,
            "data": request.purpose
        }
        
        import base64
        return base64.b64encode(json.dumps(ilp_data).encode()).decode()

    def _generate_fulfillment_condition(self) -> str:
        """Génère une condition de fulfillment"""
        # Condition simplifiée
        import base64
        import hashlib
        
        condition_data = f"fulfillment_{datetime.now().timestamp()}"
        condition_hash = hashlib.sha256(condition_data.encode()).digest()
        return base64.b64encode(condition_hash).decode()

    def _sign_request(self, data: Dict[str, Any], headers: Dict[str, str]) -> str:
        """Signe une requête avec la clé privée"""
        try:
            if not self.private_key:
                return ""
            
            # Création de la chaîne à signer
            string_to_sign = f"{headers['Date']}\n{json.dumps(data, sort_keys=True)}"
            
            # Signature
            signature = self.private_key.sign(
                string_to_sign.encode(),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            import base64
            return base64.b64encode(signature).decode()
            
        except Exception as e:
            logger.error("Erreur signature requête", error=str(e))
            return ""

    async def _simulate_transfer(self, request: MojaloopTransferRequest) -> MojaloopTransferResponse:
        """Simule un transfert Mojaloop (mode dry-run)"""
        await asyncio.sleep(2)  # Simulation délai réseau
        
        logger.info("Simulation transfert Mojaloop", 
                   transfer_id=request.id,
                   amount=request.amount,
                   currency=request.currency,
                   payer=request.payer_msisdn,
                   payee=request.payee_msisdn)
        
        return MojaloopTransferResponse(
            id=request.id,
            mojaloop_transaction_id=f"ML{request.id}",
            status="COMPLETED",
            quote_id=f"Q{request.id}",
            transfer_id=f"T{request.id}",
            settlement_completed=True,
            settlement_timestamp=datetime.now(timezone.utc),
            error_message=None
        )

    async def close(self):
        """Ferme le connecteur Mojaloop"""
        if self.session:
            await self.session.close()
            logger.info("Session Mojaloop fermée")

class MSISDNValidator:
    """Validateur MSISDN pour l'Afrique"""
    
    def validate(self, msisdn: str) -> bool:
        try:
            # Suppression des espaces et caractères spéciaux
            msisdn = ''.join(filter(str.isdigit, msisdn))
            
            # Vérification longueur (9-15 chiffres)
            if len(msisdn) < 9 or len(msisdn) > 15:
                return False
            
            # Vérification format pays (RDC: 243)
            if msisdn.startswith('243'):
                if len(msisdn) != 12:  # 243 + 9 chiffres
                    return False
            elif msisdn.startswith('0'):
                # Format local
                if len(msisdn) != 10:  # 0 + 9 chiffres
                    return False
            else:
                return False
            
            return True
            
        except Exception:
            return False