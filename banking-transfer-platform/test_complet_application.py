#!/usr/bin/env python3
"""
Test complet de l'application Banking Transfer Platform
"""

import asyncio
import subprocess
import time
import requests
import json
import sys
import os
from datetime import datetime

class ApplicationTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.backend_process = None
        
    def print_status(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {status}: {message}")
        
    def test_backend_imports(self):
        """Test des imports du backend"""
        self.print_status("Test des imports backend...")
        try:
            import sys
            sys.path.append('backend')
            
            from app.main import app
            self.print_status(f"✅ Backend importé: {len(app.routes)} routes", "SUCCESS")
            
            from app.connectors.swift_connector import SWIFTConnector
            from app.connectors.mojaloop_connector import MojaloopConnector
            self.print_status("✅ Connecteurs importés", "SUCCESS")
            
            from app.monitoring.advanced_monitoring import monitoring
            self.print_status("✅ Monitoring importé", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.print_status(f"❌ Erreur import backend: {e}", "ERROR")
            return False
    
    def test_swift_connector(self):
        """Test du connecteur SWIFT"""
        self.print_status("Test du connecteur SWIFT...")
        try:
            import sys
            sys.path.append('backend')
            
            from app.connectors.swift_connector import SWIFTConnector
            
            config = {"dry_run": True}
            connector = SWIFTConnector(config)
            
            result = asyncio.run(connector.initialize())
            if result:
                self.print_status("✅ SWIFT Connector initialisé", "SUCCESS")
            
            request = {
                "id": "TEST-001",
                "amount": 1000.0,
                "currency": "USD",
                "sender_iban": "US12345678901234567890",
                "recipient_iban": "DE12345678901234567890"
            }
            
            response = asyncio.run(connector.send_transfer(request))
            if response["status"] == "COMPLETED":
                self.print_status("✅ SWIFT transfert simulé", "SUCCESS")
                return True
            else:
                self.print_status(f"❌ SWIFT transfert échoué", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"❌ Erreur SWIFT: {e}", "ERROR")
            return False
    
    def test_mojaloop_connector(self):
        """Test du connecteur Mojaloop"""
        self.print_status("Test du connecteur Mojaloop...")
        try:
            import sys
            sys.path.append('backend')
            
            from app.connectors.mojaloop_connector import MojaloopConnector
            
            config = {"dry_run": True}
            connector = MojaloopConnector(config)
            
            result = asyncio.run(connector.initialize())
            if result:
                self.print_status("✅ Mojaloop Connector initialisé", "SUCCESS")
            
            request = {
                "id": "TEST-002",
                "amount": 50000.0,
                "currency": "CDF",
                "payer_msisdn": "243999999999",
                "payee_msisdn": "243888888888"
            }
            
            response = asyncio.run(connector.send_transfer(request))
            if response["status"] == "COMPLETED":
                self.print_status("✅ Mojaloop transfert simulé", "SUCCESS")
                return True
            else:
                self.print_status(f"❌ Mojaloop transfert échoué", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"❌ Erreur Mojaloop: {e}", "ERROR")
            return False
    
    def test_frontend_structure(self):
        """Test de la structure frontend"""
        self.print_status("Test de la structure frontend...")
        required_files = [
            "package.json",
            "public/index.html",
            "src/index.js",
            "src/App.tsx"
        ]
        
        success_count = 0
        for file_path in required_files:
            if os.path.exists(f"frontend/{file_path}"):
                self.print_status(f"✅ {file_path} existe", "SUCCESS")
                success_count += 1
            else:
                self.print_status(f"❌ {file_path} manquant", "ERROR")
        
        return success_count == len(required_files)
    
    def generate_report(self, results):
        """Génère un rapport de test"""
        self.print_status("Génération du rapport...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(results),
                "passed": sum(1 for r in results.values() if r),
                "failed": sum(1 for r in results.values() if not r)
            },
            "results": results
        }
        
        print("\n" + "="*50)
        print("RAPPORT DE TEST COMPLET")
        print("="*50)
        print(f"Tests total: {report['summary']['total_tests']}")
        print(f"Réussis: {report['summary']['passed']}")
        print(f"Échoués: {report['summary']['failed']}")
        print(f"Taux de réussite: {(report['summary']['passed']/report['summary']['total_tests']*100):.1f}%")
        print("="*50)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print("="*50)
        
        if report['summary']['failed'] == 0:
            self.print_status("🎉 TOUS LES TESTS RÉUSSIS !", "SUCCESS")
            return True
        else:
            self.print_status(f"⚠️ {report['summary']['failed']} tests échoués", "WARNING")
            return False
    
    def run_complete_test(self):
        """Exécute tous les tests"""
        self.print_status("🚀 DÉBUT DU TEST COMPLET", "INFO")
        
        results = {}
        
        try:
            # Test 1: Imports backend
            results["Backend Imports"] = self.test_backend_imports()
            
            # Test 2: Structure frontend
            results["Frontend Structure"] = self.test_frontend_structure()
            
            # Test 3: Connecteur SWIFT
            results["SWIFT Connector"] = self.test_swift_connector()
            
            # Test 4: Connecteur Mojaloop
            results["Mojaloop Connector"] = self.test_mojaloop_connector()
            
            # Génération du rapport
            success = self.generate_report(results)
            
            return success
            
        except Exception as e:
            self.print_status(f"❌ Erreur critique: {e}", "ERROR")
            return False

def main():
    """Fonction principale"""
    tester = ApplicationTester()
    
    try:
        success = tester.run_complete_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrompu par l'utilisateur")
        sys.exit(1)

if __name__ == "__main__":
    main()
