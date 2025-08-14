#!/usr/bin/env python3
"""
Démonstration de transfert réel - BCC vers Monese
"""

import asyncio
import sys
from datetime import datetime

# Ajout du backend au path
sys.path.append('backend')

from app.connectors.swift_connector import SWIFTConnector

class RealTransferDemo:
    def __init__(self):
        self.transfer_data = {
            "amount": 777.0,
            "currency": "USD",
            "sender_bic": "BCCRCD22",
            "sender_iban": "CD12345678901234567890",
            "sender_name": "Compte BCC",
            "recipient_bic": "LHVBEE22",
            "recipient_iban": "EE047700771001660150",
            "recipient_name": "Monese Ltd",
            "purpose": "Transfert personnel",
            "reference": "M40282987"
        }
    
    def print_transfer_details(self):
        print("="*70)
        print("💸 DÉMONSTRATION TRANSFERT RÉEL - BCC VERS MONESE")
        print("="*70)
        print(f"📊 Montant: {self.transfer_data['amount']} {self.transfer_data['currency']}")
        print(f"🏦 Expéditeur: {self.transfer_data['sender_name']}")
        print(f"   BIC: {self.transfer_data['sender_bic']}")
        print(f"   IBAN: {self.transfer_data['sender_iban']}")
        print(f"")
        print(f"📱 Destinataire: {self.transfer_data['recipient_name']}")
        print(f"   BIC: {self.transfer_data['recipient_bic']}")
        print(f"   IBAN: {self.transfer_data['recipient_iban']}")
        print(f"   Adresse: LHV Bank, Tartu mnt 2, 10145 Tallinn, Estonia")
        print(f"")
        print(f"📝 Référence: {self.transfer_data['reference']}")
        print(f"🎯 Objectif: {self.transfer_data['purpose']}")
        print("="*70)
    
    async def simulate_real_transfer(self):
        print("\n🚀 Simulation du transfert réel...")
        
        try:
            # Configuration SWIFT
            config = {"dry_run": True}
            connector = SWIFTConnector(config)
            
            # Initialisation
            print("📡 Initialisation du connecteur SWIFT...")
            init_result = await connector.initialize()
            if not init_result:
                print("❌ Échec d'initialisation")
                return False
            
            print("✅ Connecteur SWIFT initialisé")
            
            # Création de la demande de transfert
            transfer_request = {
                "id": f"BCC-MONESE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "amount": self.transfer_data['amount'],
                "currency": self.transfer_data['currency'],
                "sender_iban": self.transfer_data['sender_iban'],
                "recipient_iban": self.transfer_data['recipient_iban']
            }
            
            # Envoi du transfert
            print("📤 Envoi du transfert SWIFT...")
            print("⏳ Traitement en cours...")
            
            response = await connector.send_transfer(transfer_request)
            
            # Affichage du résultat
            print("\n" + "="*50)
            print("📊 RÉSULTAT DU TRANSFERT")
            print("="*50)
            
            if response["status"] == "COMPLETED":
                print("✅ TRANSFERT RÉUSSI!")
                print(f"   ID: {response['id']}")
                print(f"   Message SWIFT: {response['swift_message_id']}")
                print(f"   ACK reçu: {'Oui' if response['ack_received'] else 'Non'}")
                print(f"   Montant: {self.transfer_data['amount']} {self.transfer_data['currency']}")
                print(f"   Destinataire: {self.transfer_data['recipient_name']}")
                print(f"   Référence: {self.transfer_data['reference']}")
                return True
            else:
                print("❌ TRANSFERT ÉCHOUÉ!")
                print(f"   Erreur: {response.get('error_message', 'Erreur inconnue')}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors du transfert: {e}")
            return False
    
    def show_next_steps(self):
        print("\n💡 PROCHAINES ÉTAPES POUR TRANSFERT RÉEL:")
        print("="*50)
        print("1. 📞 Contactez votre banque BCC")
        print("2. 📋 Fournissez les informations Monese:")
        print(f"   - Destinataire: {self.transfer_data['recipient_name']}")
        print(f"   - IBAN: {self.transfer_data['recipient_iban']}")
        print(f"   - BIC: {self.transfer_data['recipient_bic']}")
        print(f"   - Référence: {self.transfer_data['reference']}")
        print(f"   - Montant: {self.transfer_data['amount']} {self.transfer_data['currency']}")
        print("3. ⏱️ Délais: 1-3 jours ouvrables")
    
    async def run_demo(self):
        print("🎯 DÉMONSTRATION TRANSFERT RÉEL - BCC → MONESE")
        print("="*60)
        
        self.print_transfer_details()
        success = await self.simulate_real_transfer()
        self.show_next_steps()
        
        return success

def main():
    demo = RealTransferDemo()
    
    try:
        success = asyncio.run(demo.run_demo())
        if success:
            print("\n🎉 DÉMONSTRATION TERMINÉE AVEC SUCCÈS!")
        else:
            print("\n⚠️ DÉMONSTRATION ÉCHOUÉE")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Démonstration interrompue")
        sys.exit(1)

if __name__ == "__main__":
    main()
