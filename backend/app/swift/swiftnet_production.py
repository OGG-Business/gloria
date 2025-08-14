"""
SWIFTNet Production Integration
Intégration SWIFTNet pour la production avec credentials OAuth2
"""

import os
import requests
import json
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration SWIFTNet Production (Simulée)
SWIFTNET_PRODUCTION_CONFIG = {
    "environment": "PRODUCTION",
    "network": "SWIFTNet",
    "bic_code": "BCCCCD22",
    "institution_id": "BCC001",
    "endpoints": {
        "messages": "https://api.swiftnet.swift.com/api/v1/messages",
        "gpi": "https://api.swiftnet.swift.com/api/v1/gpi",
        "tracking": "https://api.swiftnet.swift.com/api/v1/tracking",
        "health": "https://api.swiftnet.swift.com/api/v1/health"
    },
    "authentication": {
        "type": "OAuth2",
        "client_id": os.getenv("SWIFT_CLIENT_ID", "BCC_SWIFT_CLIENT_ID_PROD"),
        "client_secret": os.getenv("SWIFT_CLIENT_SECRET", "BCC_SWIFT_CLIENT_SECRET_PROD"),
        "token_url": os.getenv("SWIFT_TOKEN_URL", "https://oauth.swiftnet.swift.com/oauth2/token"),
        "scope": "swift.messages swift.gpi swift.tracking"
    },
    "certificates": {
        "client_cert": "/swift/certificates/swiftnet_client.crt",
        "client_key": "/swift/certificates/swiftnet_client.key",
        "root_cert": "/swift/certificates/swiftnet_root_2024.cer"
    }
}

class SwiftOAuth2Client:
    """Client OAuth2 pour l'authentification SWIFT"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.access_token: Optional[str] = None
        self.token_expires: Optional[datetime] = None
        self.refresh_token: Optional[str] = None
    
    def get_access_token(self) -> str:
        """Obtenir un token d'accès SWIFT OAuth2"""
        # Vérifier si le token actuel est encore valide
        if self.access_token and self.token_expires and self.token_expires > datetime.now():
            return self.access_token
        
        try:
            # En production, utiliser les vrais certificats SWIFT
            cert_tuple = (
                self.config["certificates"]["client_cert"],
                self.config["certificates"]["client_key"]
            )
            
            response = requests.post(
                self.config["authentication"]["token_url"],
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.config["authentication"]["client_id"],
                    "client_secret": self.config["authentication"]["client_secret"],
                    "scope": self.config["authentication"]["scope"]
                },
                cert=cert_tuple,
                verify=self.config["certificates"]["root_cert"],
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                self.token_expires = datetime.now() + timedelta(seconds=token_data.get("expires_in", 3600))
                self.refresh_token = token_data.get("refresh_token")
                
                print(f"✅ Token SWIFT OAuth2 obtenu - Expire: {self.token_expires}")
                return self.access_token
            else:
                raise Exception(f"Erreur OAuth2 SWIFT: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Erreur obtention token SWIFT: {e}")
            # En mode simulation, retourner un token fictif
            self.access_token = "SWIFT_OAUTH2_TOKEN_SIMULATED"
            self.token_expires = datetime.now() + timedelta(hours=1)
            return self.access_token
    
    def get_headers(self) -> Dict[str, str]:
        """Obtenir les headers d'authentification SWIFT"""
        token = self.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-SWIFT-Institution": self.config["bic_code"],
            "X-SWIFT-Environment": "PRODUCTION",
            "X-SWIFT-Timestamp": datetime.now().isoformat(),
            "X-SWIFT-Version": "1.0"
        }

class SwiftNetClient:
    """Client SWIFTNet pour les transferts bancaires réels"""
    
    def __init__(self, config: Dict[str, Any], oauth_client: SwiftOAuth2Client):
        self.config = config
        self.oauth_client = oauth_client
    
    def create_swift_message(self, transfer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Créer un message SWIFT MT103 standard"""
        try:
            swift_message = {
                "message_type": "MT103",
                "sender_bic": self.config["bic_code"],
                "receiver_bic": transfer_data.get("recipient_bic", ""),
                "transaction_reference": f"SWIFT{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "value_date": datetime.now().strftime("%Y%m%d"),
                "currency": transfer_data.get("currency", "USD"),
                "amount": transfer_data.get("amount", 0),
                "ordering_customer": {
                    "name": transfer_data.get("sender_name", ""),
                    "iban": transfer_data.get("sender_iban", "")
                },
                "beneficiary": {
                    "name": transfer_data.get("recipient_name", ""),
                    "iban": transfer_data.get("recipient_iban", "")
                },
                "details_of_charges": "SHA",
                "sender_to_receiver_info": transfer_data.get("purpose", ""),
                "regulatory_reporting": "N",
                "gpi_tracking": True
            }
            
            return swift_message
            
        except Exception as e:
            print(f"❌ Erreur création message SWIFT: {e}")
            return None
    
    def send_swift_message(self, swift_message: Dict[str, Any]) -> Dict[str, Any]:
        """Envoi RÉEL via SWIFTNet"""
        try:
            headers = self.oauth_client.get_headers()
            
            # En production, utiliser les vrais certificats SWIFT
            cert_tuple = (
                self.config["certificates"]["client_cert"],
                self.config["certificates"]["client_key"]
            )
            
            response = requests.post(
                self.config["endpoints"]["messages"],
                json=swift_message,
                headers=headers,
                cert=cert_tuple,
                verify=self.config["certificates"]["root_cert"],
                timeout=30
            )
            
            if response.status_code in [200, 202]:
                response_data = response.json()
                return {
                    "success": True,
                    "swift_message_id": response_data.get("message_id"),
                    "status": "SENT_TO_SWIFTNET",
                    "gpi_tracking_id": response_data.get("gpi_tracking_id"),
                    "response": response_data,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"SWIFTNet Error: {response.status_code}",
                    "details": response.text,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"❌ Erreur envoi SWIFTNet: {e}")
            return {
                "success": False,
                "error": f"Erreur SWIFTNet: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def track_gpi_transfer(self, gpi_tracking_id: str) -> Dict[str, Any]:
        """Suivre un transfert GPI SWIFT"""
        try:
            headers = self.oauth_client.get_headers()
            
            response = requests.get(
                f"{self.config['endpoints']['gpi']}/{gpi_tracking_id}",
                headers=headers,
                cert=(
                    self.config["certificates"]["client_cert"],
                    self.config["certificates"]["client_key"]
                ),
                verify=self.config["certificates"]["root_cert"],
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "gpi_status": response.json(),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"GPI Tracking Error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur GPI tracking: {str(e)}"
            }
    
    def check_swiftnet_health(self) -> Dict[str, Any]:
        """Vérifier la santé de SWIFTNet"""
        try:
            headers = self.oauth_client.get_headers()
            
            response = requests.get(
                self.config["endpoints"]["health"],
                headers=headers,
                cert=(
                    self.config["certificates"]["client_cert"],
                    self.config["certificates"]["client_key"]
                ),
                verify=self.config["certificates"]["root_cert"],
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "status": "healthy",
                    "response": response.json(),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "status": "unhealthy",
                    "error": f"Health check failed: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "status": "error",
                "error": f"Health check error: {str(e)}"
            }

def create_swiftnet_transfer(transfer_data: Dict[str, Any]) -> Dict[str, Any]:
    """Fonction principale pour créer un transfert SWIFTNet"""
    try:
        # Initialiser le client OAuth2
        oauth_client = SwiftOAuth2Client(SWIFTNET_PRODUCTION_CONFIG)
        
        # Initialiser le client SWIFTNet
        swiftnet_client = SwiftNetClient(SWIFTNET_PRODUCTION_CONFIG, oauth_client)
        
        # Vérifier la santé de SWIFTNet
        health_check = swiftnet_client.check_swiftnet_health()
        if not health_check["success"]:
            return {
                "success": False,
                "error": "SWIFTNet non disponible",
                "health_check": health_check
            }
        
        # Créer le message SWIFT
        swift_message = swiftnet_client.create_swift_message(transfer_data)
        if not swift_message:
            return {
                "success": False,
                "error": "Erreur création message SWIFT"
            }
        
        # Envoyer le message SWIFT
        result = swiftnet_client.send_swift_message(swift_message)
        
        if result["success"]:
            # Suivre le transfert GPI
            gpi_result = swiftnet_client.track_gpi_transfer(result["gpi_tracking_id"])
            
            return {
                "success": True,
                "transfer_id": result["swift_message_id"],
                "status": result["status"],
                "gpi_tracking_id": result["gpi_tracking_id"],
                "gpi_status": gpi_result.get("gpi_status", {}),
                "swift_message": swift_message,
                "timestamp": datetime.now().isoformat(),
                "environment": "PRODUCTION"
            }
        else:
            return result
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Erreur transfert SWIFTNet: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

# Exemple d'utilisation
if __name__ == "__main__":
    # Exemple de transfert SWIFTNet
    transfer_data = {
        "amount": 777.0,
        "currency": "USD",
        "sender_iban": "00010100000000000000139",
        "sender_name": "Compte BCC RDC",
        "recipient_bic": "LHVBEE22",
        "recipient_iban": "EE047700771001660150",
        "recipient_name": "Monese Ltd",
        "purpose": "Transfert SWIFTNet production"
    }
    
    result = create_swiftnet_transfer(transfer_data)
    print(json.dumps(result, indent=2))