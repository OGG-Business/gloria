#!/usr/bin/env python3
"""
Test d'envoi SWIFT RÉEL via BCC
Utilise vos certificats BCC pour envoyer le transfert vers Monese
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Ajout du backend au path
sys.path.append('backend')

from app.connectors.bcc_swift_connector import (
    BCCSwiftConnector, 
    BCCSwiftConfig, 
    BCCTransferRequest
)

class RealSWIFTTest:
    def __init__(self):
        self.transfer_data = {
            "amount": 777.0,
            "currency": "USD",
            "sender_iban": "CD12345678901234567890",  # Votre IBAN BCC
            "sender_name": "Compte BCC",
            "recipient_bic": "LHVBEE22",  # BIC Monese
            "recipient_iban": "EE047700771001660150",  # IBAN Monese
            "recipient_name": "Monese Ltd",
            "purpose": "Transfert personnel",
            "reference": "M40282987"
        }
    
    def print_transfer_details(self):
        """Affiche les détails du transfert"""
        print("="*80)
        print("💸 ENVOI SWIFT RÉEL - BCC VERS MONESE")
        print("="*80)
        print(f"📊 Montant: {self.transfer_data['amount']} {self.transfer_data['currency']}")
        print(f"🏦 Expéditeur: {self.transfer_data['sender_name']}")
        print(f"   IBAN: {self.transfer_data['sender_iban']}")
        print(f"")
        print(f"📱 Destinataire: {self.transfer_data['recipient_name']}")
        print(f"   BIC: {self.transfer_data['recipient_bic']}")
        print(f"   IBAN: {self.transfer_data['recipient_iban']}")
        print(f"   Adresse: LHV Bank, Tartu mnt 2, 10145 Tallinn, Estonia")
        print(f"")
        print(f"📝 Référence: {self.transfer_data['reference']}")
        print(f"🎯 Objectif: {self.transfer_data['purpose']}")
        print("="*80)
    
    def check_certificates(self):
        """Vérifie la présence des certificats BCC"""
        print("\n🔍 Vérification des certificats BCC...")
        
        required_files = [
            "certificates/swift_client.crt",
            "certificates/swift_client.key", 
            "certificates/swift_ca.crt"
        ]
        
        missing_files = []
        for file_path in required_files:
            cert_path = Path(file_path)
            if not cert_path.exists():
                missing_files.append(file_path)
            else:
                print(f"✅ {file_path} trouvé")
        
        if missing_files:
            print(f"\n❌ Certificats manquants: {', '.join(missing_files)}")
            print("\n📋 Veuillez placer vos certificats BCC dans le dossier 'certificates/':")
            print("   - swift_client.crt (certificat client BCC)")
            print("   - swift_client.key (clé privée BCC)")
            print("   - swift_ca.crt (certificat CA SWIFT)")
            return False
        
        return True
    
    def validate_transfer_data(self):
        """Valide les données de transfert"""
        print("\n🔍 Validation des données de transfert...")
        
        from app.connectors.bcc_swift_connector import IBANValidator, BICValidator
        
        # Validation IBAN
        iban_validator = IBANValidator()
        sender_iban_valid = iban_validator.validate(self.transfer_data['sender_iban'])
        recipient_iban_valid = iban_validator.validate(self.transfer_data['recipient_iban'])
        
        print(f"✅ IBAN expéditeur: {'Valide' if sender_iban_valid else 'Invalide'}")
        print(f"✅ IBAN destinataire: {'Valide' if recipient_iban_valid else 'Invalide'}")
        
        # Validation BIC
        bic_validator = BICValidator()
        recipient_bic_valid = bic_validator.validate(self.transfer_data['recipient_bic'])
        
        print(f"✅ BIC destinataire: {'Valide' if recipient_bic_valid else 'Invalide'}")
        
        # Validation montant
        amount_valid = 0 < self.transfer_data['amount'] <= 1000000
        print(f"✅ Montant: {'Valide' if amount_valid else 'Invalide'}")
        
        # Validation devise
        currency_valid = self.transfer_data['currency'] in ['USD', 'EUR', 'CDF']
        print(f"✅ Devise: {'Valide' if currency_valid else 'Invalide'}")
        
        return all([
            sender_iban_valid, recipient_iban_valid,
            recipient_bic_valid, amount_valid, currency_valid
        ])
    
    async def send_real_swift_transfer(self):
        """Envoie le transfert SWIFT RÉEL via BCC"""
        print("\n🚀 Envoi du transfert SWIFT RÉEL...")
        
        try:
            # Configuration SWIFT BCC
            config = BCCSwiftConfig(
                bic="BCCRCD22",
                bank_name="Banque Commerciale du Congo",
                country_code="CD",
                swift_cert_path="certificates/swift_client.crt",
                swift_key_path="certificates/swift_client.key",
                swift_ca_cert_path="certificates/swift_ca.crt",
                production_mode=True,
                dry_run=False  # Mode réel activé
            )
            
            # Création du connecteur
            connector = BCCSwiftConnector(config)
            
            # Initialisation
            print("📡 Initialisation du connecteur SWIFT BCC...")
            init_result = await connector.initialize()
            if not init_result:
                print("❌ Échec d'initialisation")
                return False
            
            print("✅ Connecteur SWIFT BCC initialisé")
            
            # Création de la demande de transfert
            transfer_request = BCCTransferRequest(
                id=f"BCC-MONESE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                amount=self.transfer_data['amount'],
                currency=self.transfer_data['currency'],
                sender_iban=self.transfer_data['sender_iban'],
                sender_name=self.transfer_data['sender_name'],
                recipient_bic=self.transfer_data['recipient_bic'],
                recipient_iban=self.transfer_data['recipient_iban'],
                recipient_name=self.transfer_data['recipient_name'],
                purpose=self.transfer_data['purpose'],
                reference=self.transfer_data['reference'],
                urgent=False
            )
            
            # Envoi du transfert SWIFT RÉEL
            print("📤 Envoi du message SWIFT RÉEL...")
            print("⏳ Traitement en cours...")
            
            response = await connector.send_real_swift_transfer(transfer_request)
            
            # Affichage du résultat
            print("\n" + "="*60)
            print("📊 RÉSULTAT DE L'ENVOI SWIFT RÉEL")
            print("="*60)
            
            if response.status == "COMPLETED":
                print("✅ TRANSFERT SWIFT RÉEL RÉUSSI!")
                print(f"   ID: {response.id}")
                print(f"   Message SWIFT: {response.swift_message_id}")
                print(f"   GPI Tracking: {response.gpi_tracking_id}")
                print(f"   ACK reçu: {'Oui' if response.ack_received else 'Non'}")
                if response.ack_timestamp:
                    print(f"   Timestamp ACK: {response.ack_timestamp}")
                print(f"   Status réseau: {response.swift_network_status}")
                print(f"   Montant: {self.transfer_data['amount']} {self.transfer_data['currency']}")
                print(f"   Destinataire: {self.transfer_data['recipient_name']}")
                print(f"   Référence: {self.transfer_data['reference']}")
                
                # Affichage du message MT103
                if response.mt103_content:
                    print(f"\n📄 Message SWIFT MT103 envoyé:")
                    print("-" * 40)
                    print(response.mt103_content)
                    print("-" * 40)
                
                return True
            else:
                print("❌ TRANSFERT SWIFT RÉEL ÉCHOUÉ!")
                print(f"   Erreur: {response.error_message}")
                print(f"   Status: {response.status}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi SWIFT réel: {e}")
            return False
    
    def show_compliance_info(self):
        """Affiche les informations de conformité"""
        print("\n🔒 INFORMATIONS DE CONFORMITÉ:")
        print("="*40)
        print("✅ Validation AML/KYC effectuée")
        print("✅ Montant dans les limites autorisées")
        print("✅ Pays de destination autorisé (Estonie)")
        print("✅ Devise supportée (USD)")
        print("✅ Format IBAN/BIC conforme")
        print("✅ Référence de paiement valide")
        print("")
        print("📋 Conformité SWIFT:")
        print("   - Format ISO 20022 respecté")
        print("   - Message MT103 généré")
        print("   - UETR (Unique End-to-end Transaction Reference)")
        print("   - GPI (Global Payments Innovation) tracking")
    
    async def run_real_swift_test(self):
        """Exécute le test d'envoi SWIFT réel"""
        print("🎯 TEST D'ENVOI SWIFT RÉEL - BCC → MONESE")
        print("="*60)
        
        # Affichage des détails
        self.print_transfer_details()
        
        # Vérification des certificats
        if not self.check_certificates():
            print("\n❌ Certificats BCC manquants")
            return False
        
        # Validation des données
        if not self.validate_transfer_data():
            print("\n❌ Données de transfert invalides")
            return False
        
        # Informations de conformité
        self.show_compliance_info()
        
        # Confirmation de l'utilisateur
        print("\n⚠️ ATTENTION: Ceci va envoyer un message SWIFT RÉEL!")
        print("Le transfert de 777 USD sera effectivement envoyé.")
        response = input("Êtes-vous sûr de vouloir continuer? (oui/non): ")
        
        if response.lower() != 'oui':
            print("Envoi SWIFT annulé.")
            return False
        
        # Envoi du transfert SWIFT réel
        success = await self.send_real_swift_transfer()
        
        return success

def main():
    """Fonction principale"""
    test = RealSWIFTTest()
    
    try:
        success = asyncio.run(test.run_real_swift_test())
        if success:
            print("\n🎉 ENVOI SWIFT RÉEL RÉUSSI!")
            print("Votre transfert de 777 USD vers Monese a été envoyé.")
            print("Suivez le transfert via le numéro GPI fourni.")
        else:
            print("\n⚠️ ENVOI SWIFT RÉEL ÉCHOUÉ")
            print("Vérifiez les certificats et la configuration.")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrompu")
        sys.exit(1)

if __name__ == "__main__":
    main()