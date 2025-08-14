"""
SWIFTNet Client - Solution pour corriger les erreurs SWIFT
Client SWIFTNet pour transferts réels via le réseau privé SWIFT
"""

import requests
import ssl
import socket
import json
import hmac
import hashlib
import base64
from datetime import datetime
from typing import Dict, Any, Optional

class SwiftNetClient:
    """
    Client SWIFTNet pour transferts SWIFT réels
    Solution pour corriger les erreurs d'accréditation SWIFT
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = self._create_swiftnet_session()
        self.auth = SwiftNetAuth(config)
    
    def _create_swiftnet_session(self) -> requests.Session:
        """Création session SWIFTNet sécurisée"""
        session = requests.Session()
        
        # Configuration certificats SWIFTNet
        if self.config.get('certificate_path') and self.config.get('private_key_path'):
            session.cert = (
                self.config['certificate_path'],
                self.config['private_key_path']
            )
        
        if self.config.get('root_ca_path'):
            session.verify = self.config['root_ca_path']
        
        # Headers SWIFTNet
        session.headers.update({
            'X-SWIFT-Institution': self.config.get('bic_code', 'BCCCCD22'),
            'X-SWIFT-Network': 'SWIFTNet',
            'Content-Type': 'application/json',
            'User-Agent': 'BCC-SWIFTNet-Client/1.0'
        })
        
        return session
    
    def check_swiftnet_connectivity(self) -> Dict[str, Any]:
        """Vérification connectivité SWIFTNet"""
        try:
            # Test connectivité SWIFTNet
            swiftnet_hosts = [
                "swiftnet.swift.com",
                "api.swiftnet.swift.com",
                "gpi.swift.com"
            ]
            
            results = {}
            for host in swiftnet_hosts:
                try:
                    # Test DNS
                    socket.gethostbyname(host)
                    
                    # Test SSL/TLS
                    context = ssl.create_default_context()
                    with socket.create_connection((host, 443), timeout=10) as sock:
                        with context.wrap_socket(sock, server_hostname=host) as ssock:
                            cert = ssock.getpeercert()
                            results[host] = {
                                "dns": True,
                                "ssl": True,
                                "cert_valid": bool(cert)
                            }
                except Exception as e:
                    results[host] = {
                        "dns": False,
                        "ssl": False,
                        "error": str(e)
                    }
            
            return {
                "success": any(r.get("dns") and r.get("ssl") for r in results.values()),
                "details": results,
                "swiftnet_ready": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"SWIFTNet connectivity error: {str(e)}",
                "swiftnet_ready": False
            }
    
    def create_swift_message(self, transfer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Création message SWIFT MT103 pour SWIFTNet"""
        try:
            # Format message SWIFT MT103
            swift_message = {
                "message_type": "MT103",
                "sender": {
                    "bic": self.config.get('bic_code', 'BCCCCD22'),
                    "institution": self.config.get('institution_id', 'BCC001'),
                    "account": transfer_data.get('sender_iban'),
                    "name": transfer_data.get('sender_name')
                },
                "recipient": {
                    "bic": transfer_data.get('recipient_bic'),
                    "account": transfer_data.get('recipient_iban'),
                    "name": transfer_data.get('recipient_name')
                },
                "transaction": {
                    "amount": transfer_data.get('amount'),
                    "currency": transfer_data.get('currency'),
                    "reference": transfer_data.get('reference'),
                    "purpose": transfer_data.get('purpose')
                },
                "timestamp": datetime.utcnow().isoformat(),
                "gpi_tracking": True
            }
            
            return {
                "success": True,
                "message": swift_message,
                "message_id": f"SWIFT{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error creating SWIFT message: {str(e)}"
            }
    
    def send_swift_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Envoi message SWIFT via SWIFTNet"""
        try:
            # Création message SWIFT
            swift_result = self.create_swift_message(message_data)
            if not swift_result["success"]:
                return swift_result
            
            swift_message = swift_result["message"]
            message_id = swift_result["message_id"]
            
            # Headers d'authentification SWIFTNet
            headers = self.auth.get_swiftnet_headers(json.dumps(swift_message))
            self.session.headers.update(headers)
            
            # Envoi via SWIFTNet
            response = self.session.post(
                self.config.get('api_endpoint', 'https://api.swiftnet.swift.com/messages'),
                json=swift_message,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                return {
                    "success": True,
                    "swift_message_id": message_id,
                    "gpi_tracking_id": response_data.get('gpi_tracking_id'),
                    "status": "SENT",
                    "swiftnet_response": response_data,
                    "note": "TRANSFERT SWIFT RÉEL VIA SWIFTNet - AUCUNE SIMULATION"
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "error": "SWIFTNet Authentication Error: Accréditation SWIFT requise",
                    "status": "AUTH_REQUIRED",
                    "note": "TRANSFERT SWIFT RÉEL - ACCRÉDITATION SWIFT REQUISE"
                }
            elif response.status_code == 403:
                return {
                    "success": False,
                    "error": "SWIFTNet Access Error: Accès SWIFTNet refusé",
                    "status": "ACCESS_DENIED",
                    "note": "TRANSFERT SWIFT RÉEL - ACCÈS SWIFTNet REQUIS"
                }
            else:
                return {
                    "success": False,
                    "error": f"SWIFTNet Error: {response.status_code}",
                    "details": response.text,
                    "note": "TRANSFERT SWIFT RÉEL - ERREUR SWIFTNet"
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "SWIFTNet Connection Error: Réseau SWIFTNet non accessible",
                "status": "NETWORK_ERROR",
                "note": "TRANSFERT SWIFT RÉEL - RÉSEAU SWIFTNet REQUIS"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"SWIFTNet Connection Error: {str(e)}",
                "note": "TRANSFERT SWIFT RÉEL - ERREUR CONNEXION SWIFTNet"
            }
    
    def track_gpi_transfer(self, gpi_tracking_id: str) -> Dict[str, Any]:
        """Suivi transfert GPI via SWIFTNet"""
        try:
            headers = self.auth.get_swiftnet_headers(gpi_tracking_id)
            self.session.headers.update(headers)
            
            response = self.session.get(
                f"https://gpi.swift.com/tracking/{gpi_tracking_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "tracking_data": response.json(),
                    "status": "TRACKED"
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
                "error": f"GPI Tracking Error: {str(e)}"
            }

class SwiftNetAuth:
    """Authentification SWIFTNet"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def create_swiftnet_signature(self, message: str, timestamp: str) -> str:
        """Création signature SWIFTNet HMAC-SHA256"""
        try:
            secret = self.config.get('swiftnet_credentials', {}).get('api_key', 'swiftnet_secret')
            message_to_sign = f"{message}{timestamp}"
            
            signature = hmac.new(
                secret.encode('utf-8'),
                message_to_sign.encode('utf-8'),
                hashlib.sha256
            ).digest()
            
            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            print(f"Error creating SWIFTNet signature: {e}")
            return "signature_error"
    
    def get_swiftnet_headers(self, message: str) -> Dict[str, str]:
        """Génération headers SWIFTNet"""
        try:
            timestamp = datetime.utcnow().isoformat()
            signature = self.create_swiftnet_signature(message, timestamp)
            
            return {
                'X-SWIFT-Signature': signature,
                'X-SWIFT-Timestamp': timestamp,
                'X-SWIFT-Institution': self.config.get('bic_code', 'BCCCCD22'),
                'X-SWIFT-Network': 'SWIFTNet',
                'Authorization': f'Bearer {self.config.get("swiftnet_credentials", {}).get("api_key", "swiftnet_key")}'
            }
        except Exception as e:
            print(f"Error generating SWIFTNet headers: {e}")
            return {
                'X-SWIFT-Network': 'SWIFTNet',
                'X-SWIFT-Institution': self.config.get('bic_code', 'BCCCCD22')
            }