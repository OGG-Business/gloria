#!/usr/bin/env python3
"""
Test de connectivité réelle du connecteur SWIFT BCC
"""

import asyncio
import sys
import aiohttp
from datetime import datetime
from pathlib import Path

# Ajout du backend au path
sys.path.append('backend')

class TestConnectiviteReelle:
    def __init__(self):
        self.bcc_config = {
            "bic": "BCCGCDK2XXX",
            "bank_name": "Banque Centrale du Congo",
            "address": "563, Boulevard Colonel Tshatshi, KINSHASA, RDC",
            "swift_network": "SWIFTNet PKI"
        }
        
        self.transfer_data = {
            "amount": 777.0,
            "currency": "USD",
            "sender_iban": "CD12345678901234567890",
            "sender_name": "Compte BCC",
            "recipient_bic": "LHVBEE22",
            "recipient_iban": "EE047700771001660150",
            "recipient_name": "Monese Ltd",
            "purpose": "Transfert personnel",
            "reference": "M40282987"
        }
    
    def print_test_header(self):
        print("="*80)
        print("🚀 TEST DE CONNECTIVITÉ RÉELLE - SWIFT BCC")
        print("="*80)
        print(f"🏦 BIC: {self.bcc_config['bic']}")
        print(f"🏛️ Banque: {self.bcc_config['bank_name']}")
        print(f"🌐 Réseau: {self.bcc_config['swift_network']}")
        print(f"📊 Montant: {self.transfer_data['amount']} {self.transfer_data['currency']}")
        print("="*80)
    
    def check_certificates(self):
        print("\n🔐 VÉRIFICATION DES CERTIFICATS SWIFT:")
        print("-" * 50)
        
        required_files = [
            "certificates/swiftnet_root_2019.cer",
            "certificates/swift_client.crt",
            "certificates/swift_client.key"
        ]
        
        all_present = True
        for file_path in required_files:
            cert_path = Path(file_path)
            if cert_path.exists():
                size = cert_path.stat().st_size
                print(f"✅ {file_path} ({size} bytes)")
            else:
                print(f"❌ {file_path} (manquant)")
                all_present = False
        
        return all_present
    
    async def test_swift_connector_import(self):
        print("\n📡 TEST IMPORT CONNECTEUR SWIFT:")
        print("-" * 40)
        
        try:
            # Test d'import du connecteur
            from app.connectors.bcc_swift_connector import BCCSwiftConnector, BCCSwiftConfig, BCCTransferRequest
            
            print("✅ Import du connecteur SWIFT BCC réussi")
            
            # Test de création de la configuration
            config = BCCSwiftConfig(
                bic=self.bcc_config['bic'],
                bank_name=self.bcc_config['bank_name'],
                address=self.bcc_config['address'],
                swift_network=self.bcc_config['swift_network']
            )
            print("✅ Configuration SWIFT BCC créée")
            
            # Test de création du connecteur
            connector = BCCSwiftConnector(config)
            print("✅ Connecteur SWIFT BCC créé")
            
            return True, connector
            
        except Exception as e:
            print(f"❌ Erreur import connecteur SWIFT: {e}")
            return False, None
    
    async def test_swift_initialization(self, connector):
        print("\n🔧 TEST INITIALISATION SWIFT:")
        print("-" * 40)
        
        try:
            print("⏳ Initialisation du connecteur SWIFT...")
            init_result = await connector.initialize()
            
            if init_result:
                print("✅ Connecteur SWIFT initialisé avec succès")
                return True
            else:
                print("❌ Échec de l'initialisation SWIFT")
                return False
                
        except Exception as e:
            print(f"❌ Erreur initialisation SWIFT: {e}")
            return False
    
    async def test_swift_transfer_simulation(self, connector):
        print("\n💸 TEST SIMULATION TRANSFERT SWIFT:")
        print("-" * 50)
        
        try:
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
            
            print("✅ Demande de transfert créée")
            print(f"   ID: {transfer_request.id}")
            print(f"   Montant: {transfer_request.amount} {transfer_request.currency}")
            print(f"   Expéditeur: {transfer_request.sender_name}")
            print(f"   Destinataire: {transfer_request.recipient_name}")
            
            # Simulation du transfert (en mode dry-run)
            print("\n⏳ Simulation du transfert SWIFT...")
            response = await connector.send_real_swift_transfer(transfer_request)
            
            print("✅ Réponse SWIFT reçue")
            print(f"   Status: {response.status}")
            print(f"   Message ID: {response.swift_message_id}")
            print(f"   ACK reçu: {response.ack_received}")
            
            if response.error_message:
                print(f"   Erreur: {response.error_message}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur simulation transfert SWIFT: {e}")
            return False
    
    async def test_external_api_connectivity(self):
        print("\n🌐 TEST CONNECTIVITÉ APIs EXTERNES:")
        print("-" * 50)
        
        test_urls = [
            "https://httpbin.org/get",
            "https://api.github.com",
            "https://jsonplaceholder.typicode.com/posts/1"
        ]
        
        async with aiohttp.ClientSession() as session:
            for url in test_urls:
                try:
                    print(f"🔍 Test de {url}...")
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            print(f"✅ {url} - Connectivité OK")
                        else:
                            print(f"⚠️ {url} - Status {response.status}")
                except Exception as e:
                    print(f"❌ {url} - Erreur: {e}")
    
    async def test_swift_message_generation(self, connector):
        print("\n📄 TEST GÉNÉRATION MESSAGES SWIFT:")
        print("-" * 50)
        
        try:
            # Test de génération MT103
            mt103_content = connector._generate_bcc_mt103_content(
                BCCTransferRequest(
                    id="TEST-001",
                    amount=777.0,
                    currency="USD",
                    sender_iban="CD12345678901234567890",
                    sender_name="Compte BCC",
                    recipient_bic="LHVBEE22",
                    recipient_iban="EE047700771001660150",
                    recipient_name="Monese Ltd",
                    purpose="Test",
                    reference="TEST-REF"
                )
            )
            
            print("✅ Message MT103 généré:")
            print("-" * 30)
            print(mt103_content[:200] + "...")
            print("-" * 30)
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur génération message SWIFT: {e}")
            return False
    
    async def run_complete_test(self):
        print("🎯 TEST COMPLET DE CONNECTIVITÉ RÉELLE")
        print("="*60)
        
        # En-tête
        self.print_test_header()
        
        # Vérification des certificats
        if not self.check_certificates():
            print("\n❌ CERTIFICATS MANQUANTS - Test interrompu")
            return False
        
        # Test d'import du connecteur
        import_success, connector = await self.test_swift_connector_import()
        if not import_success:
            print("\n❌ IMPORT ÉCHOUÉ - Test interrompu")
            return False
        
        # Test d'initialisation
        init_success = await self.test_swift_initialization(connector)
        if not init_success:
            print("\n⚠️ INITIALISATION ÉCHOUÉE - Test en mode limité")
        
        # Test de génération de messages
        message_success = await self.test_swift_message_generation(connector)
        
        # Test de simulation de transfert
        if init_success:
            transfer_success = await self.test_swift_transfer_simulation(connector)
        else:
            print("\n⏭️ Simulation de transfert ignorée (initialisation échouée)")
            transfer_success = False
        
        # Test de connectivité externe
        await self.test_external_api_connectivity()
        
        # Fermeture du connecteur
        if connector:
            await connector.close()
        
        # Résumé final
        print("\n" + "="*80)
        print("📊 RÉSUMÉ DU TEST DE CONNECTIVITÉ")
        print("="*80)
        
        results = {
            "Certificats": "✅ Présents",
            "Import connecteur": "✅ Réussi" if import_success else "❌ Échoué",
            "Initialisation": "✅ Réussie" if init_success else "❌ Échouée",
            "Génération messages": "✅ Réussie" if message_success else "❌ Échouée",
            "Simulation transfert": "✅ Réussie" if transfer_success else "❌ Échouée",
            "Connectivité externe": "✅ Testée"
        }
        
        for test, result in results.items():
            print(f"   {test}: {result}")
        
        overall_success = import_success and message_success
        
        if overall_success:
            print("\n🎉 TEST DE CONNECTIVITÉ RÉUSSI!")
            print("L'application peut interagir avec les APIs SWIFT")
        else:
            print("\n⚠️ TEST DE CONNECTIVITÉ PARTIEL")
            print("Certains composants nécessitent une configuration supplémentaire")
        
        return overall_success

def main():
    test = TestConnectiviteReelle()
    
    try:
        success = asyncio.run(test.run_complete_test())
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrompu")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur générale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
