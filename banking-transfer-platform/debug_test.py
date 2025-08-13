#!/usr/bin/env python3
import requests
import json

transfer_data = {
    "amount": 777.0,
    "currency": "USD",
    "sender_iban": "00010100000000000000139",
    "sender_name": "Compte BCC RDC",
    "recipient_bic": "LHVBEE22",
    "recipient_iban": "EE047700771001660150",
    "recipient_name": "Monese Ltd",
    "purpose": "Test"
}

print("🔍 DEBUG TEST - Transfert SWIFT...")

try:
    response = requests.post(
        "http://localhost:8000/api/transfers",
        json=transfer_data,
        timeout=30
    )
    
    print(f"📊 Status Code: {response.status_code}")
    print(f"📋 Response Text (raw): {repr(response.text)}")
    print(f"📋 Response Text (normal): {response.text}")
    
    if response.status_code == 500:
        try:
            error_data = response.json()
            print(f"📋 Error JSON: {json.dumps(error_data, indent=2)}")
            
            detail = error_data.get('detail', '')
            print(f"📝 Detail (raw): {repr(detail)}")
            print(f"📝 Detail (normal): {detail}")
            print(f"📝 Detail length: {len(detail)}")
            
            search_term = "TRANSFERT SWIFT RÉEL - AUCUNE SIMULATION"
            print(f"🔍 Recherche: '{search_term}'")
            print(f"🔍 Dans detail: {search_term in detail}")
            
        except Exception as e:
            print(f"❌ Erreur parsing JSON: {e}")
            
except Exception as e:
    print(f"❌ Erreur requête: {e}")
