#!/usr/bin/env python3
"""
Test Debug SWIFT 404 - Débogage de l'erreur SWIFT 404
Test direct pour identifier la source exacte de l'erreur 404
"""

import requests
import json
from datetime import datetime

def test_debug_swift_404():
    print("🔍 DEBUG SWIFT 404")
    print("="*80)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("="*80)
    
    # Test direct de l'endpoint de transfert
    transfer_data = {
        "amount": 777.0,
        "currency": "USD",
        "sender_iban": "00010100000000000000139",
        "sender_name": "Compte BCC RDC",
        "recipient_bic": "LHVBEE22",
        "recipient_iban": "EE047700771001660150",
        "recipient_name": "Monese Ltd",
        "purpose": "Debug SWIFT 404",
        "reference": "M40282987"
    }
    
    print("\n📋 Test direct du transfert SWIFT...")
    print("   💰 Montant: 777.00 USD")
    print("   🏦 Expéditeur: Compte BCC RDC")
    print("   🏛️ Destinataire: Monese Ltd")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/transfers",
            json=transfer_data,
            timeout=30
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📝 Headers: {dict(response.headers)}")
        
        if response.status_code == 500:
            try:
                data = response.json()
                error_detail = data.get('detail', '')
                print(f"📝 Erreur complète: {error_detail}")
                
                # Analyse détaillée de l'erreur
                if 'SWIFT API Error: 404' in error_detail:
                    print("\n🔍 ANALYSE ERREUR 404:")
                    print("   ❌ Erreur 404 détectée")
                    print("   🔍 Recherche de la source...")
                    
                    # Vérification des logs du backend
                    print("\n📋 VÉRIFICATION BACKEND:")
                    print("   🔍 Test de l'endpoint /api/swift/status...")
                    
                    status_response = requests.get("http://localhost:8000/api/swift/status", timeout=10)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"   ✅ SWIFT Status: {status_data}")
                    else:
                        print(f"   ❌ SWIFT Status: {status_response.status_code}")
                    
                    # Test de l'endpoint racine
                    print("\n📋 Test de l'endpoint racine...")
                    root_response = requests.get("http://localhost:8000/", timeout=10)
                    if root_response.status_code == 200:
                        root_data = root_response.json()
                        print(f"   ✅ Root: {root_data}")
                    else:
                        print(f"   ❌ Root: {root_response.status_code}")
                    
                    # Test direct des endpoints SWIFT
                    print("\n📋 Test direct des endpoints SWIFT...")
                    swift_endpoints = [
                        "https://api.swift.com",
                        "https://www.swift.com",
                        "https://developer.swift.com"
                    ]
                    
                    for endpoint in swift_endpoints:
                        try:
                            test_response = requests.get(endpoint, timeout=10)
                            print(f"   🔍 {endpoint}: {test_response.status_code}")
                        except Exception as e:
                            print(f"   ❌ {endpoint}: {str(e)}")
                    
                    print("\n🔍 CONCLUSION:")
                    print("   ⚠️ L'erreur 404 provient probablement de:")
                    print("      1. L'ancienne URL SWIFT encore utilisée")
                    print("      2. Le backend non redémarré")
                    print("      3. La fonction non mise à jour")
                    
                else:
                    print("\n✅ Pas d'erreur 404 détectée")
                    
            except Exception as e:
                print(f"   ❌ Erreur parsing: {e}")
        else:
            print(f"   ✅ Status code inattendu: {response.status_code}")
            try:
                data = response.json()
                print(f"   📝 Réponse: {data}")
            except:
                print(f"   📝 Réponse: {response.text}")
                
    except Exception as e:
        print(f"   ❌ Erreur test: {e}")

if __name__ == "__main__":
    try:
        print("🚀 Démarrage du debug SWIFT 404...")
        test_debug_swift_404()
    except Exception as e:
        print(f"\n❌ ERREUR GÉNÉRALE: {e}")