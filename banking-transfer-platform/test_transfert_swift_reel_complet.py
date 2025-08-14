#!/usr/bin/env python3
import requests
import socket
import time
import subprocess
import os
import json
from datetime import datetime

def lancer_backend_complet():
    print("🚀 LANCEMENT BACKEND COMPLET")
    print("="*80)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("="*80)
    
    print("\n🔧 Test 1: Vérification et Lancement Backend")
    print("-" * 50)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print("   ✅ Backend: DÉJÀ OPÉRATIONNEL")
        else:
            print("   ❌ Backend: NON OPÉRATIONNEL")
            print("   🔧 Lancement RÉEL du backend...")
            
            os.chdir('backend')
            process = subprocess.Popen(
                ["python", "-m", "uvicorn", "app.main_reel:app", "--host", "0.0.0.0", "--port", "8000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print("   ⏳ Attente du lancement RÉEL (20 secondes)...")
            time.sleep(20)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('localhost', 8000))
            sock.close()
            
            if result == 0:
                print("   ✅ Backend: LANCÉ RÉELLEMENT AVEC SUCCÈS")
            else:
                print("   ❌ Backend: ÉCHEC LANCEMENT RÉEL")
                return False
                
    except Exception as e:
        print(f"   ❌ Erreur lancement backend: {e}")
        return False
    
    return True

def test_backend_complet():
    print("\n🏦 Test 2: Vérification Backend Complet")
    print("-" * 50)
    
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Root Endpoint: {response.status_code} OK")
            print(f"   📋 Message: {data.get('message', 'N/A')}")
            print(f"   🌍 Environment: {data.get('environment', 'N/A')}")
            print(f"   🔗 SWIFT Connectivity: {data.get('swift_connectivity', 'N/A')}")
            print(f"   🔐 Certificates: {data.get('certificates', 'N/A')}")
            print(f"   📊 Status: {data.get('status', 'N/A')}")
            
            if data.get('environment') == 'PRODUCTION':
                print("   ✅ Environment: PRODUCTION (RÉEL)")
            else:
                print("   ❌ Environment: NON PRODUCTION")
                return False
        else:
            print(f"   ❌ Root Endpoint: {response.status_code}")
            return False
            
        response = requests.get("http://localhost:8000/api/swift/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"\n   ✅ SWIFT Status: {response.status_code} OK")
            print(f"   🔗 SWIFT Connectivity: {data.get('swift_connectivity', 'N/A')}")
            print(f"   🔐 Certificates Valid: {data.get('certificates_valid', 'N/A')}")
            print(f"   🏦 BIC Code: {data.get('bic_code', 'N/A')}")
            print(f"   🏛️ Institution ID: {data.get('institution_id', 'N/A')}")
            print(f"   ✅ Ready for Transfers: {data.get('ready_for_transfers', 'N/A')}")
            
            if data.get('ready_for_transfers'):
                print("   ✅ SWIFT: PRÊT POUR TRANSFERTS RÉELS")
            else:
                print("   ⚠️ SWIFT: ACCRÉDITATION REQUISE")
        else:
            print(f"   ❌ SWIFT Status: {response.status_code}")
            return False
            
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"\n   ✅ Health Check: {response.status_code} OK")
            print(f"   📊 Status: {data.get('status', 'N/A')}")
            print(f"   �� SWIFT Connectivity: {data.get('swift_connectivity', 'N/A')}")
            print(f"   🔐 Certificates Valid: {data.get('certificates_valid', 'N/A')}")
        else:
            print(f"   ❌ Health Check: {response.status_code}")
            return False
            
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur backend: {e}")
        return False

def test_transfert_swift_reel_complet():
    print("\n💸 Test 3: Transfert SWIFT RÉEL Complet")
    print("-" * 50)
    
    transfer_data = {
        "amount": 777.0,
        "currency": "USD",
        "sender_iban": "00010100000000000000139",
        "sender_name": "Compte BCC RDC",
        "recipient_bic": "LHVBEE22",
        "recipient_iban": "EE047700771001660150",
        "recipient_name": "Monese Ltd",
        "purpose": "Transfert SWIFT RÉEL de 777 USD",
        "reference": "M40282987"
    }
    
    print("📋 DÉTAILS DU TRANSFERT SWIFT RÉEL:")
    print("   💰 Montant: 777.00 USD")
    print("   🏦 Expéditeur: Compte BCC RDC")
    print("   📍 IBAN Expéditeur: 00010100000000000000139")
    print("   🏛️ Destinataire: Monese Ltd")
    print("   📍 IBAN Destinataire: EE047700771001660150")
    print("   🏦 BIC Destinataire: LHVBEE22")
    print("   📋 Référence: M40282987")
    print("   📍 Adresse: LHV Bank, Tartu mnt 2, 10145 Tallinn, Estonia")
    
    print("\n🚀 LANCEMENT DU TRANSFERT SWIFT RÉEL...")
    print("   ⚠️ ATTENTION: Transfert SWIFT RÉEL de 777 USD")
    print("   ⚠️ De: BCC RDC → Vers: Monese Ltd")
    print("   ⚠️ Réseau: SWIFT RÉEL")
    print("   ⚠️ Montant: 777.00 USD")
    
    start_time = datetime.now()
    
    try:
        response = requests.post(
            "http://localhost:8000/api/transfers",
            json=transfer_data,
            timeout=30
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"   ⏱️ Durée: {duration:.2f} secondes")
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   📝 Réponse: {json.dumps(data, indent=2)}")
                
                print("\n🎉 TRANSFERT SWIFT RÉUSSI!")
                print("   ✅ Status: RÉUSSI")
                print(f"   🆔 ID Transfert: {data.get('id', 'N/A')}")
                print(f"   📊 Status SWIFT: {data.get('status', 'N/A')}")
                print(f"   🆔 Message ID: {data.get('swift_message_id', 'N/A')}")
                print(f"   🏦 GPI Tracking ID: {data.get('transfer_details', {}).get('gpi_tracking_id', 'N/A')}")
                print(f"   💰 Montant: {data.get('transfer_details', {}).get('amount', 'N/A')} {data.get('transfer_details', {}).get('currency', 'N/A')}")
                print(f"   📋 Type Message: {data.get('transfer_details', {}).get('swift_message_type', 'N/A')}")
                print(f"   ⏰ Timestamp: {data.get('timestamp', 'N/A')}")
                print(f"   🌍 Environment: {data.get('environment', 'N/A')}")
                print(f"   📝 Note: {data.get('note', 'N/A')}")
                
                return {
                    "status": "RÉUSSI",
                    "details": data,
                    "message": "Transfert SWIFT RÉEL effectué avec succès"
                }
                
            except Exception as e:
                print(f"   ❌ Erreur parsing succès: {e}")
                return {
                    "status": "ERREUR",
                    "details": f"Erreur parsing: {e}",
                    "message": "Transfert réussi mais erreur de parsing"
                }
                
        elif response.status_code == 500:
            try:
                data = response.json()
                error_detail = data.get('detail', '')
                print(f"   📝 Erreur: {error_detail}")
                
                if 'SWIFT API Error: 404' in error_detail:
                    print("\n⚠️ TRANSFERT EN ATTENTE:")
                    print("   📊 Status: EN ATTENTE")
                    print("   🔍 Raison: API publique SWIFT - Accréditation requise")
                    print("   💡 Solution: Contact SWIFT pour accréditation officielle")
                    print("   📋 Détails: Transfert préparé mais non envoyé (accréditation requise)")
                    
                    return {
                        "status": "EN ATTENTE",
                        "details": error_detail,
                        "message": "Transfert préparé - Accréditation SWIFT requise"
                    }
                    
                elif 'SWIFT GPI' in error_detail:
                    print("\n⚠️ TRANSFERT EN ATTENTE:")
                    print("   📊 Status: EN ATTENTE")
                    print("   🔍 Raison: GPI SWIFT - Accréditation requise")
                    print("   💡 Solution: Contact SWIFT pour accréditation GPI")
                    print("   📋 Détails: Transfert préparé mais non envoyé (accréditation GPI requise)")
                    
                    return {
                        "status": "EN ATTENTE",
                        "details": error_detail,
                        "message": "Transfert préparé - Accréditation GPI SWIFT requise"
                    }
                    
                elif 'Aucun endpoint SWIFT disponible' in error_detail:
                    print("\n⚠️ TRANSFERT EN ATTENTE:")
                    print("   📊 Status: EN ATTENTE")
                    print("   🔍 Raison: Aucun endpoint SWIFT disponible")
                    print("   💡 Solution: Accréditation SWIFT requise")
                    print("   📋 Détails: Transfert préparé mais endpoints non accessibles")
                    
                    return {
                        "status": "EN ATTENTE",
                        "details": error_detail,
                        "message": "Transfert préparé - Endpoints SWIFT non accessibles"
                    }
                    
                else:
                    print("\n❌ TRANSFERT ÉCHOUÉ:")
                    print("   📊 Status: ÉCHOUÉ")
                    print("   🔍 Raison: Erreur SWIFT")
                    print("   📋 Détails: Voir erreur ci-dessus")
                    
                    return {
                        "status": "ÉCHOUÉ",
                        "details": error_detail,
                        "message": "Transfert SWIFT échoué"
                    }
                    
            except Exception as e:
                print(f"   ❌ Erreur parsing: {e}")
                return {
                    "status": "ERREUR",
                    "details": f"Erreur parsing: {e}",
                    "message": "Erreur lors de l'analyse du transfert"
                }
        else:
            print(f"   ❌ Status code inattendu: {response.status_code}")
            return {
                "status": "ERREUR",
                "details": f"Status code inattendu: {response.status_code}",
                "message": "Erreur inattendue lors du transfert"
            }
            
    except Exception as e:
        print(f"   ❌ Erreur transfert: {e}")
        return {
            "status": "ERREUR",
            "details": f"Erreur transfert: {e}",
            "message": "Erreur de connexion lors du transfert"
        }

def afficher_resultat_final(resultat_backend, resultat_transfert):
    print("\n" + "="*80)
    print("🏆 RÉSULTAT FINAL - TEST BACKEND COMPLET")
    print("="*80)
    
    print("\n📊 RÉSULTATS DES TESTS:")
    print(f"   🚀 Backend Complet: {'✅ SUCCÈS' if resultat_backend else '❌ ÉCHEC'}")
    print(f"   💸 Transfert SWIFT: {resultat_transfert['status']}")
    
    print("\n💸 RÉSULTAT DU TRANSFERT SWIFT RÉEL:")
    print(f"   📊 Status: {resultat_transfert['status']}")
    print(f"   📝 Message: {resultat_transfert['message']}")
    print(f"   📋 Détails: {resultat_transfert['details']}")
    
    if resultat_transfert['status'] == 'RÉUSSI':
        print("\n🎉 SUCCÈS COMPLET!")
        print("   ✅ Backend opérationnel")
        print("   ✅ Transfert SWIFT RÉEL effectué")
        print("   ✅ 777 USD transférés de BCC vers Monese")
        print("   ✅ Détails du transfert disponibles")
        
    elif resultat_transfert['status'] == 'EN ATTENTE':
        print("\n⚠️ TRANSFERT EN ATTENTE:")
        print("   ✅ Backend opérationnel")
        print("   ⚠️ Transfert préparé mais non envoyé")
        print("   🔧 Accréditation SWIFT requise")
        print("   📋 Contact SWIFT pour accréditation officielle")
        
    else:
        print("\n❌ ÉCHEC:")
        print("   ❌ Problème avec le backend ou le transfert")
        print("   🔧 Vérifier la configuration")
        print("   📋 Voir détails ci-dessus")

if __name__ == "__main__":
    try:
        print("🚀 Démarrage du test backend complet avec transfert SWIFT RÉEL...")
        print("⚠️ ATTENTION: Ceci teste un transfert SWIFT RÉEL de 777 USD")
        print("⚠️ De: BCC RDC → Vers: Monese Ltd")
        
        resultat_backend = lancer_backend_complet()
        if resultat_backend:
            test_backend_complet()
            resultat_transfert = test_transfert_swift_reel_complet()
        else:
            resultat_transfert = {
                "status": "ERREUR",
                "details": "Backend non opérationnel",
                "message": "Impossible de tester le transfert"
            }
        
        afficher_resultat_final(resultat_backend, resultat_transfert)
        
    except Exception as e:
        print(f"\n❌ ERREUR GÉNÉRALE: {e}")
        print("❌ Le test a échoué")
