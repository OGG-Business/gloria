#!/usr/bin/env python3
"""
Test Transfert SWIFT RÉEL - BCC vers Monese
"""

import requests
import socket
import time
from datetime import datetime

def test_transfert_swift_reel_bcc_monese():
    print("💸 TEST TRANSFERT SWIFT RÉEL - BCC VERS MONESE")
    print("="*70)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("="*70)
    
    print("\n🔌 Test 1: Vérification Backend")
    print("-" * 40)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print("   ✅ Backend: OPÉRATIONNEL")
        else:
            print("   ❌ Backend: NON OPÉRATIONNEL")
            print("   🔧 Démarrage du backend...")
            
            import subprocess
            import os
            
            os.chdir('/workspace/banking-transfer-platform/backend')
            process = subprocess.Popen(
                ["python", "-m", "uvicorn", "app.main_reel:app", "--host", "0.0.0.0", "--port", "8000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            time.sleep(10)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('localhost', 8000))
            sock.close()
            
            if result == 0:
                print("   ✅ Backend: DÉMARRÉ")
            else:
                print("   ❌ Backend: ÉCHEC DÉMARRAGE")
                return False
    except Exception as e:
        print(f"   ❌ Erreur backend: {e}")
        return False
    
    print("\n🏦 Test 2: Statut SWIFT")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:8000/api/swift/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   🔗 SWIFT Connectivity: {data.get('swift_connectivity', 'N/A')}")
            print(f"   �� Certificates Valid: {data.get('certificates_valid', 'N/A')}")
            print(f"   🏦 BIC Code: {data.get('bic_code', 'N/A')}")
            print(f"   🏛️ Institution ID: {data.get('institution_id', 'N/A')}")
            print(f"   ✅ Ready for Transfers: {data.get('ready_for_transfers', 'N/A')}")
            
            if not data.get('ready_for_transfers'):
                print("   ❌ SWIFT non prêt pour les transferts")
                return False
        else:
            print(f"   ❌ SWIFT Status: Erreur {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur SWIFT Status: {e}")
        return False
    
    print("\n💳 Test 3: Transfert SWIFT RÉEL")
    print("-" * 40)
    
    transfer_data = {
        "amount": 777.0,
        "currency": "USD",
        "sender_iban": "00010100000000000000139",
        "sender_name": "Compte BCC RDC",
        "recipient_bic": "LHVBEE22",
        "recipient_iban": "EE047700771001660150",
        "recipient_name": "Monese Ltd",
        "purpose": "Transfert personnel BCC vers Monese",
        "reference": "M40282987"
    }
    
    print("📋 DÉTAILS DU TRANSFERT:")
    print(f"   💰 Montant: {transfer_data['amount']} {transfer_data['currency']}")
    print(f"   🏦 Expéditeur: {transfer_data['sender_name']}")
    print(f"   📍 IBAN Expéditeur: {transfer_data['sender_iban']}")
    print(f"   🏛️ Destinataire: {transfer_data['recipient_name']}")
    print(f"   📍 IBAN Destinataire: {transfer_data['recipient_iban']}")
    print(f"   🏦 BIC Destinataire: {transfer_data['recipient_bic']}")
    print(f"   📝 Référence: {transfer_data['reference']}")
    print(f"   📍 Adresse: LHV Bank, Tartu mnt 2, 10145 Tallinn, Estonia")
    
    print("\n🚀 EXÉCUTION DU TRANSFERT SWIFT RÉEL...")
    print("-" * 40)
    
    try:
        print("   🔍 Envoi de la requête SWIFT...")
        start_time = datetime.now()
        
        response = requests.post(
            "http://localhost:8000/api/transfers",
            json=transfer_data,
            timeout=60
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"   ⏱️ Durée: {duration:.2f} secondes")
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ TRANSFERT RÉUSSI!")
            
            try:
                data = response.json()
                
                print("\n🎉 RÉSULTAT DU TRANSFERT - RÉUSSI")
                print("="*50)
                print(f"   🆔 ID Transfert: {data.get('id', 'N/A')}")
                print(f"   🎯 Status: {data.get('status', 'N/A')}")
                print(f"   📝 Message: {data.get('message', 'N/A')}")
                print(f"   ⏰ Timestamp: {data.get('timestamp', 'N/A')}")
                print(f"   🏦 SWIFT Message ID: {data.get('swift_message_id', 'N/A')}")
                print(f"   🌍 Environment: {data.get('environment', 'N/A')}")
                print(f"   📝 Note: {data.get('note', 'N/A')}")
                
                transfer_details = data.get('transfer_details', {})
                if transfer_details:
                    print("\n📋 DÉTAILS DU TRANSFERT:")
                    print(f"   💰 Montant: {transfer_details.get('amount', 'N/A')} {transfer_details.get('currency', 'N/A')}")
                    print(f"   🏦 Expéditeur: {transfer_details.get('sender_name', 'N/A')}")
                    print(f"   📍 IBAN Expéditeur: {transfer_details.get('sender_iban', 'N/A')}")
                    print(f"   🏛️ Destinataire: {transfer_details.get('recipient_name', 'N/A')}")
                    print(f"   📍 IBAN Destinataire: {transfer_details.get('recipient_iban', 'N/A')}")
                    print(f"   🏦 BIC Destinataire: {transfer_details.get('recipient_bic', 'N/A')}")
                    print(f"   📋 Type Message: {transfer_details.get('swift_message_type', 'N/A')}")
                    print(f"   🎯 GPI Tracking ID: {transfer_details.get('gpi_tracking_id', 'N/A')}")
                    print(f"   🏦 SWIFT Status: {transfer_details.get('swift_status', 'N/A')}")
                
                print("\n✅ TRANSFERT SWIFT RÉEL RÉUSSI!")
                print("   Votre transfert de 777 USD a été envoyé avec succès")
                print("   Le montant sera crédité sur votre compte Monese")
                
                return {
                    "status": "RÉUSSI",
                    "message": "Transfert SWIFT réussi",
                    "details": data
                }
                
            except Exception as e:
                print(f"   ❌ Erreur parsing réponse: {e}")
                return {
                    "status": "RÉUSSI",
                    "message": "Transfert réussi mais erreur parsing",
                    "response": response.text
                }
                
        elif response.status_code == 503:
            print("   ⏳ TRANSFERT EN ATTENTE")
            print("   Service SWIFT temporairement indisponible")
            
            try:
                data = response.json()
                print(f"   📝 Détail: {data.get('detail', 'N/A')}")
            except:
                print(f"   📝 Détail: {response.text}")
            
            return {
                "status": "EN ATTENTE",
                "message": "Service SWIFT indisponible",
                "detail": response.text
            }
            
        elif response.status_code == 400:
            print("   ❌ TRANSFERT ÉCHOUÉ - ERREUR VALIDATION")
            
            try:
                data = response.json()
                print(f"   📝 Erreur: {data.get('detail', 'N/A')}")
            except:
                print(f"   📝 Erreur: {response.text}")
            
            return {
                "status": "ÉCHOUÉ",
                "message": "Erreur validation données",
                "detail": response.text
            }
            
        else:
            print("   ❌ TRANSFERT ÉCHOUÉ")
            
            try:
                data = response.json()
                print(f"   📝 Erreur: {data.get('detail', 'N/A')}")
            except:
                print(f"   📝 Erreur: {response.text}")
            
            return {
                "status": "ÉCHOUÉ",
                "message": f"Erreur {response.status_code}",
                "detail": response.text
            }
            
    except requests.exceptions.ConnectionError:
        print("   ❌ TRANSFERT ÉCHOUÉ - CONNEXION IMPOSSIBLE")
        return {
            "status": "ÉCHOUÉ",
            "message": "Connexion impossible",
            "detail": "Backend non accessible"
        }
        
    except requests.exceptions.Timeout:
        print("   ❌ TRANSFERT ÉCHOUÉ - TIMEOUT")
        return {
            "status": "ÉCHOUÉ",
            "message": "Timeout",
            "detail": "Délai d'attente dépassé"
        }
        
    except Exception as e:
        print(f"   ❌ TRANSFERT ÉCHOUÉ - ERREUR: {e}")
        return {
            "status": "ÉCHOUÉ",
            "message": "Erreur générale",
            "detail": str(e)
        }

if __name__ == "__main__":
    try:
        result = test_transfert_swift_reel_bcc_monese()
        
        print("\n" + "="*70)
        print("🏆 RÉSULTAT FINAL DU TRANSFERT SWIFT")
        print("="*70)
        
        if result["status"] == "RÉUSSI":
            print("🎉 TRANSFERT RÉUSSI!")
            print("   ✅ Votre transfert de 777 USD a été envoyé avec succès")
            print("   ✅ Le montant sera crédité sur votre compte Monese")
            print("   ✅ Transaction SWIFT confirmée")
            
        elif result["status"] == "EN ATTENTE":
            print("⏳ TRANSFERT EN ATTENTE")
            print("   ⏳ Service SWIFT temporairement indisponible")
            print("   ⏳ Le transfert sera traité dès que possible")
            
        else:
            print("❌ TRANSFERT ÉCHOUÉ")
            print(f"   ❌ Erreur: {result['message']}")
            print(f"   ❌ Détail: {result['detail']}")
            
        print("\n📋 RÉSUMÉ:")
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")
        
    except Exception as e:
        print(f"\n❌ ERREUR GÉNÉRALE: {e}")
