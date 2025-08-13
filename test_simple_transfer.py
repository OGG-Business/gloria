#!/usr/bin/env python3
import requests
import json

# Test simple du transfert
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

print("🚀 Test simple du transfert SWIFT...")

try:
    response = requests.post(
        "http://localhost:8000/api/transfers",
        json=transfer_data,
        timeout=30
    )
    
    print(f"📊 Status Code: {response.status_code}")
    print(f"📋 Headers: {dict(response.headers)}")
    print(f"📝 Response Text: {response.text}")
    
    if response.status_code == 500:
        try:
            error_data = response.json()
            print(f"📋 Error JSON: {json.dumps(error_data, indent=2)}")
            
            detail = error_data.get('detail', '')
            print(f"📝 Detail: {detail}")
            
            if 'TRANSFERT SWIFT RÉEL - AUCUNE SIMULATION' in detail:
                print("✅ Note RÉELLE trouvée!")
            else:
                print("❌ Note RÉELLE manquante")
                
        except Exception as e:
            print(f"❌ Erreur parsing JSON: {e}")
            
except Exception as e:
    print(f"❌ Erreur requête: {e}")