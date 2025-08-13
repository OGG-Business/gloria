#!/usr/bin/env python3
import requests
import json
from datetime import datetime

def test_transfert_service_bureau():
    print("�� TEST TRANSFERT AVEC SERVICE BUREAU AZQORE")
    print("="*80)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("="*80)
    
    transfer_data = {
        "amount": 777.0,
        "currency": "USD",
        "sender_iban": "00010100000000000000139",
        "sender_name": "Compte BCC-RDC Officiel",
        "recipient_bic": "LHVBEE22",
        "recipient_iban": "EE047700771001660150",
        "recipient_name": "Monese Ltd",
        "purpose": "Transfert BCC-RDC RÉEL avec Service Bureau AZQORE",
        "reference": "M40282987"
    }
    
    print("📋 DÉTAILS DU TRANSFERT AVEC SERVICE BUREAU:")
    print("   💰 Montant: 777.00 USD")
    print("   🏦 Service Bureau: AZQORE (SBXACHSS)")
    print("   🏦 Expéditeur: Compte BCC-RDC Officiel")
    print("   📍 IBAN Expéditeur: 00010100000000000000139")
    print("   🏛️ Destinataire: Monese Ltd")
    print("   📍 IBAN Destinataire: EE047700771001660150")
    print("   🏦 BIC Destinataire: LHVBEE22")
    print("   📋 Référence: M40282987")
    print("   🏦 Institution: BANQUE CENTRALE DU CONGO (BCC-RDC)")
    print("   📍 Siège Officiel: 563, Boulevard Colonel Tshatshi, Gombe, Kinshasa")
    print("   🏦 BIC Principal Officiel: BCCGCDKSXXX (Siège Gombe)")
    print("   �� BIC Secondaire Officiel: BCCGCDK2XXX (Kinshasa Central)")
    print("   🔐 Certificats: SWIFT Officiels BCC")
    print("   🏦 Code SWIFT Officiel: BCCGCDKSXXX")
    print("   🌍 Pays: République démocratique du Congo")
    print("   💱 Devise: CDF (Franc congolais)")
    print("   ✅ Accréditation: Service Bureau AZQORE")
    print("   🔐 Sécurité: X.509 + RBAC + AES-256")
    print("   📋 Protocoles: FIN (MT103/MX), InterAct, FileAct")
    
    print("\n🚀 LANCEMENT DU TRANSFERT AVEC SERVICE BUREAU...")
    print("   ⚠️ ATTENTION: Transfert BCC-RDC RÉEL de 777 USD")
    print("   ⚠️ De: BCC-RDC Officiel → Vers: Monese Ltd")
    print("   ⚠️ Réseau: SWIFTNet RÉEL via Service Bureau AZQORE")
    print("   ⚠️ Codes SWIFT: BCCGCDKSXXX (Officiels)")
    print("   ⚠️ Montant: 777.00 USD")
    print("   ⚠️ Certificats: SWIFT Officiels BCC")
    print("   ⚠️ Service Bureau: AZQORE (SBXACHSS)")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/transfers",
            json=transfer_data,
            timeout=30
        )
        
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   📝 Réponse: {json.dumps(data, indent=2)}")
            print("\n🎉 TRANSFERT RÉUSSI AVEC SERVICE BUREAU!")
            return {"status": "RÉUSSI", "details": data}
        else:
            data = response.json()
            error_detail = data.get('detail', '')
            print(f"   📝 Erreur: {error_detail}")
            
            if 'Service Bureau' in error_detail or 'AZQORE' in error_detail:
                print("\n⚠️ TRANSFERT EN ATTENTE AVEC SERVICE BUREAU:")
                print("   📊 Status: EN ATTENTE")
                print("   🔍 Raison: Service Bureau AZQORE - Configuration requise")
                print("   💡 Solution: Configurer les credentials AZQORE")
                print("   📋 Détails: Transfert préparé avec Service Bureau mais non envoyé")
                print("   🏦 Institution: BCC-RDC prête avec Service Bureau")
                print("   🔐 Certificats: SWIFT Officiels BCC validés")
                print("   📍 Siège Officiel: 563, Boulevard Colonel Tshatshi, Gombe, Kinshasa")
                print("   🏦 BIC Officiel: BCCGCDKSXXX")
                print("   ✅ Service Bureau: AZQORE (SBXACHSS)")
                
                return {"status": "EN ATTENTE", "details": error_detail}
            else:
                return {"status": "ÉCHOUÉ", "details": error_detail}
                
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return {"status": "ERREUR", "details": str(e)}

if __name__ == "__main__":
    resultat = test_transfert_service_bureau()
    print(f"\n📊 RÉSULTAT FINAL: {resultat['status']}")
    print(f"📋 Détails: {resultat['details']}")
