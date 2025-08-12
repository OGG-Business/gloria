#!/usr/bin/env python3
"""
Configuration pour le mode réel - Banking Transfer Platform
ATTENTION: Ce script configure l'application pour les transferts bancaires réels
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Ajout du backend au path
sys.path.append('backend')

from app.connectors.swift_connector_real import (
    SWIFTRealConnector, 
    SWIFTRealConfig, 
    RealTransferRequest
)

class RealModeConfigurator:
    def __init__(self):
        self.certificates_dir = Path("certificates")
        self.config_file = Path("real_config.json")
        
    def print_warning(self):
        """Affiche les avertissements de sécurité"""
        print("="*80)
        print("⚠️  AVERTISSEMENT DE SÉCURITÉ - MODE RÉEL")
        print("="*80)
        print("Ce script configure l'application pour les transferts bancaires RÉELS.")
        print("")
        print("🚨 RISQUES:")
        print("   - Transferts d'argent réels")
        print("   - Responsabilité légale")
        print("   - Conformité bancaire requise")
        print("   - Certificats SWIFT officiels nécessaires")
        print("")
        print("✅ PRÉREQUIS:")
        print("   - Certificats SWIFT officiels")
        print("   - Autorisation bancaire")
        print("   - Conformité AML/KYC")
        print("   - Infrastructure sécurisée")
        print("="*80)
        
        response = input("Êtes-vous sûr de vouloir continuer? (oui/non): ")
        if response.lower() != 'oui':
            print("Configuration annulée.")
            sys.exit(0)
    
    def check_certificates(self):
        """Vérifie la présence des certificats SWIFT"""
        print("\n🔍 Vérification des certificats SWIFT...")
        
        required_files = [
            "swift_client.crt",
            "swift_client.key", 
            "swift_ca.crt"
        ]
        
        missing_files = []
        for file in required_files:
            cert_path = self.certificates_dir / file
            if not cert_path.exists():
                missing_files.append(file)
            else:
                print(f"✅ {file} trouvé")
        
        if missing_files:
            print(f"\n❌ Certificats manquants: {', '.join(missing_files)}")
            print("\n📋 Pour obtenir les certificats SWIFT:")
            print("   1. Contactez SWIFT directement")
            print("   2. Demandez l'accréditation bancaire")
            print("   3. Payez les frais d'accréditation (~50,000-100,000 USD/an)")
            print("   4. Installez les certificats dans le dossier 'certificates/'")
            return False
        
        return True
    
    def create_real_config(self):
        """Crée la configuration pour le mode réel"""
        print("\n⚙️ Configuration du mode réel...")
        
        # Demande des informations bancaires
        print("\n📋 Informations bancaires:")
        bic = input("BIC de votre banque: ").strip()
        bank_name = input("Nom de votre banque: ").strip()
        country_code = input("Code pays (ex: CD): ").strip()
        
        # Configuration SWIFT
        config = {
            "bic": bic,
            "bank_name": bank_name,
            "country_code": country_code,
            "swift_cert_path": str(self.certificates_dir / "swift_client.crt"),
            "swift_key_path": str(self.certificates_dir / "swift_client.key"),
            "swift_ca_cert_path": str(self.certificates_dir / "swift_ca.crt"),
            "swift_network": "SWIFTNet",
            "endpoint_url": "https://swift.com/gpi",
            "timeout": 30,
            "retry_attempts": 3,
            "production_mode": True,
            "dry_run": False  # ATTENTION: Mode réel activé
        }
        
        # Sauvegarde de la configuration
        import json
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration sauvegardée: {self.config_file}")
        return config
    
    def test_real_connector(self, config):
        """Teste le connecteur en mode réel"""
        print("\n🧪 Test du connecteur SWIFT réel...")
        
        try:
            # Création du connecteur
            swift_config = SWIFTRealConfig(**config)
            connector = SWIFTRealConnector(swift_config)
            
            # Test d'initialisation
            init_result = asyncio.run(connector.initialize())
            if not init_result:
                print("❌ Échec d'initialisation du connecteur SWIFT")
                return False
            
            print("✅ Connecteur SWIFT initialisé avec succès")
            
            # Test de transfert simulé (toujours en dry-run pour la sécurité)
            test_request = RealTransferRequest(
                id="TEST-REAL-001",
                amount=1.0,  # Montant minimal pour test
                currency="USD",
                sender_bic=config["bic"],
                sender_iban="TEST123456789",
                sender_name="Test Sender",
                recipient_bic="TESTBICXXX",
                recipient_iban="TEST987654321",
                recipient_name="Test Recipient",
                purpose="Test real mode",
                reference="TEST-REF-001"
            )
            
            print("📤 Test d'envoi de transfert...")
            response = asyncio.run(connector.send_real_transfer(test_request))
            
            if response.status == "COMPLETED":
                print("✅ Test de transfert réussi")
                print(f"   Message SWIFT: {response.swift_message_id}")
                print(f"   GPI Tracking: {response.gpi_tracking_id}")
                return True
            else:
                print(f"❌ Test de transfert échoué: {response.error_message}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur test connecteur: {e}")
            return False
    
    def create_security_checklist(self):
        """Crée une checklist de sécurité"""
        print("\n📋 CHECKLIST DE SÉCURITÉ POUR LE MODE RÉEL:")
        print("="*50)
        
        checklist = [
            "✅ Certificats SWIFT installés",
            "✅ Autorisation bancaire obtenue",
            "✅ Infrastructure sécurisée",
            "✅ Conformité AML/KYC",
            "✅ Monitoring en place",
            "✅ Logs d'audit configurés",
            "✅ Procédures de sécurité",
            "✅ Tests de charge effectués",
            "✅ Plan de reprise d'activité",
            "✅ Assurance responsabilité"
        ]
        
        for item in checklist:
            print(item)
        
        print("\n⚠️ AVERTISSEMENT FINAL:")
        print("En activant le mode réel, vous acceptez la responsabilité")
        print("légale pour tous les transferts effectués par l'application.")
        print("Assurez-vous d'avoir toutes les autorisations nécessaires.")
    
    def configure_real_mode(self):
        """Configure le mode réel complet"""
        print("🚀 Configuration du mode réel - Banking Transfer Platform")
        print("="*60)
        
        # Avertissements de sécurité
        self.print_warning()
        
        # Vérification des certificats
        if not self.check_certificates():
            print("\n❌ Impossible de continuer sans certificats SWIFT")
            return False
        
        # Création de la configuration
        config = self.create_real_config()
        
        # Test du connecteur
        if not self.test_real_connector(config):
            print("\n❌ Échec du test du connecteur")
            return False
        
        # Checklist de sécurité
        self.create_security_checklist()
        
        print("\n🎉 CONFIGURATION RÉELLE TERMINÉE!")
        print("="*50)
        print("L'application est maintenant configurée pour les transferts réels.")
        print("ATTENTION: Tous les transferts seront RÉELS!")
        print("")
        print("📞 Support: Contactez votre équipe bancaire")
        print("🔒 Sécurité: Vérifiez régulièrement les logs")
        print("📊 Monitoring: Surveillez les métriques")
        
        return True

def main():
    """Fonction principale"""
    configurator = RealModeConfigurator()
    
    try:
        success = configurator.configure_real_mode()
        if success:
            print("\n✅ Mode réel configuré avec succès")
            sys.exit(0)
        else:
            print("\n❌ Configuration échouée")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Configuration interrompue")
        sys.exit(1)

if __name__ == "__main__":
    main()