#!/usr/bin/env python3
"""
Test Application Simple
"""

import requests
import time
from datetime import datetime

def test_application_simple():
    print("🧪 TEST APPLICATION SIMPLE")
    print("="*50)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("="*50)
    
    print("\n🔧 Test 1: Backend Health")
    print("-" * 30)
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ Backend: OPÉRATIONNEL")
            print(f"   📊 Status: {response.status_code}")
            print(f"   📄 Response: {response.json()}")
        else:
            print(f"   ❌ Backend: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Backend: Erreur - {e}")
    
    print("\n🚀 Test 2: API Health")
    print("-" * 30)
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ API Health: OPÉRATIONNELLE")
            print(f"   📊 Status: {response.status_code}")
            print(f"   📄 Response: {response.json()}")
        else:
            print(f"   ❌ API Health: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ API Health: Erreur - {e}")
    
    print("\n💸 Test 3: API Transfers")
    print("-" * 30)
    try:
        transfer_data = {
            "amount": 777.0,
            "currency": "USD",
            "recipient_iban": "EE047700771001660150",
            "recipient_name": "Monese Ltd"
        }
        
        response = requests.post(
            "http://localhost:8000/api/transfers",
            json=transfer_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ API Transfers: OPÉRATIONNELLE")
            print(f"   📊 Status: {response.status_code}")
            print(f"   📄 Transfert créé: {result.get('id', 'N/A')}")
            print(f"   💰 Montant: {result.get('transfer_details', {}).get('amount', 'N/A')}")
            print(f"   🏦 Destinataire: {result.get('transfer_details', {}).get('recipient_name', 'N/A')}")
        else:
            print(f"   ❌ API Transfers: Status {response.status_code}")
            print(f"   📄 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ API Transfers: Erreur - {e}")
    
    print("\n🏠 Test 4: Root Endpoint")
    print("-" * 30)
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            print("   ✅ Root: OPÉRATIONNEL")
            print(f"   📊 Status: {response.status_code}")
            print(f"   📄 Response: {response.json()}")
        else:
            print(f"   ❌ Root: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Root: Erreur - {e}")
    
    print("\n" + "="*50)
    print("🏆 RÉSULTAT FINAL")
    print("="*50)
    print("🎯 L'application est maintenant testée!")
    print("📊 Vérifiez les résultats ci-dessus")
    print("🚀 Si tous les tests sont ✅, l'application est opérationnelle!")

if __name__ == "__main__":
    test_application_simple()
