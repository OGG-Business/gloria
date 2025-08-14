#!/usr/bin/env python3
"""
Script de lancement robuste pour Banking Transfer Platform
Teste et lance tous les composants avec gestion d'erreurs complète
"""

import subprocess
import time
import requests
import json
import sys
import os
import signal
import threading
from pathlib import Path
from typing import Optional, Dict, List

class BankingTransferLauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.test_results = {}
        self.is_running = False
        
    def print_status(self, message: str, status: str = "INFO"):
        """Affiche un message avec statut coloré"""
        colors = {
            "INFO": "\033[94m",    # Bleu
            "SUCCESS": "\033[92m", # Vert
            "ERROR": "\033[91m",   # Rouge
            "WARNING": "\033[93m", # Jaune
            "RESET": "\033[0m"     # Reset
        }
        timestamp = time.strftime("%H:%M:%S")
        print(f"{colors.get(status, '')}[{timestamp}] [{status}]{colors['RESET']} {message}")

    def test_backend_import(self) -> bool:
        """Teste l'import du backend"""
        try:
            self.print_status("Test de l'import du backend...", "INFO")
            
            # Ajoute le répertoire backend au path
            backend_path = Path("backend")
            if not backend_path.exists():
                self.print_status("Répertoire backend non trouvé", "ERROR")
                return False
            
            sys.path.insert(0, str(backend_path))
            
            # Test des imports
            from app.main import app
            from app.config import get_settings
            
            settings = get_settings()
            routes_count = len(app.routes)
            
            self.print_status(f"Backend importé avec succès", "SUCCESS")
            self.print_status(f"Application: {app.title}", "INFO")
            self.print_status(f"Version: {app.version}", "INFO")
            self.print_status(f"Routes: {routes_count} disponibles", "INFO")
            self.print_status(f"Config: {settings.app_name}", "INFO")
            
            self.test_results['backend_import'] = True
            return True
            
        except Exception as e:
            self.print_status(f"Erreur import backend: {e}", "ERROR")
            self.test_results['backend_import'] = False
            return False

    def test_frontend_config(self) -> bool:
        """Teste la configuration frontend"""
        try:
            self.print_status("Test de la configuration frontend...", "INFO")
            
            frontend_path = Path("frontend/package.json")
            if not frontend_path.exists():
                self.print_status("package.json non trouvé", "ERROR")
                self.test_results['frontend_config'] = False
                return False
            
            with open(frontend_path, 'r') as f:
                config = json.load(f)
            
            self.print_status(f"Frontend configuré: {config['name']}", "SUCCESS")
            self.print_status(f"Version: {config['version']}", "INFO")
            self.print_status(f"Dépendances: {len(config['dependencies'])} packages", "INFO")
            self.print_status(f"Proxy: {config.get('proxy', 'Non configuré')}", "INFO")
            
            self.test_results['frontend_config'] = True
            return True
            
        except Exception as e:
            self.print_status(f"Erreur config frontend: {e}", "ERROR")
            self.test_results['frontend_config'] = False
            return False

    def test_infrastructure(self) -> bool:
        """Teste l'infrastructure"""
        try:
            self.print_status("Test de l'infrastructure...", "INFO")
            
            # Test Docker
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.print_status("Docker installé", "SUCCESS")
                self.test_results['docker'] = True
            else:
                self.print_status("Docker non disponible", "WARNING")
                self.test_results['docker'] = False
            
            # Test Docker Compose
            result = subprocess.run(['docker-compose', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.print_status("Docker Compose installé", "SUCCESS")
                self.test_results['docker_compose'] = True
            else:
                self.print_status("Docker Compose non disponible", "WARNING")
                self.test_results['docker_compose'] = False
            
            # Test Makefile
            makefile_path = Path("Makefile")
            if makefile_path.exists():
                self.print_status("Makefile présent", "SUCCESS")
                self.test_results['makefile'] = True
            else:
                self.print_status("Makefile manquant", "WARNING")
                self.test_results['makefile'] = False
            
            return True
            
        except Exception as e:
            self.print_status(f"Erreur infrastructure: {e}", "ERROR")
            return False

    def launch_backend(self) -> Optional[subprocess.Popen]:
        """Lance le backend"""
        try:
            self.print_status("Lancement du backend...", "INFO")
            
            # Change vers le répertoire backend
            backend_path = Path("backend")
            if not backend_path.exists():
                self.print_status("Répertoire backend non trouvé", "ERROR")
                return None
            
            os.chdir(backend_path)
            
            # Lance uvicorn avec gestion d'erreurs
            process = subprocess.Popen([
                'python', '-m', 'uvicorn', 'app.main:app',
                '--host', '0.0.0.0', '--port', '8000',
                '--log-level', 'info'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Attend que le serveur démarre
            time.sleep(5)
            
            # Teste l'API
            try:
                response = requests.get('http://localhost:8000/', timeout=10)
                if response.status_code == 200:
                    self.print_status("Backend lancé et accessible", "SUCCESS")
                    self.print_status(f"Réponse: {response.json()}", "INFO")
                    self.test_results['backend_api'] = True
                    return process
                else:
                    self.print_status(f"Backend répond avec code: {response.status_code}", "WARNING")
                    self.test_results['backend_api'] = False
                    return process
            except requests.exceptions.RequestException as e:
                self.print_status(f"Backend non accessible: {e}", "WARNING")
                self.test_results['backend_api'] = False
                return process
                
        except Exception as e:
            self.print_status(f"Erreur lancement backend: {e}", "ERROR")
            self.test_results['backend_api'] = False
            return None

    def test_api_endpoints(self) -> Dict[str, bool]:
        """Teste tous les endpoints API"""
        endpoints = [
            ('/', 'Root'),
            ('/health', 'Health'),
            ('/auth/', 'Auth'),
            ('/accounts/', 'Accounts'),
            ('/transfers/', 'Transfers'),
            ('/kyc/', 'KYC'),
            ('/notifications/', 'Notifications'),
            ('/admin/', 'Admin'),
            ('/docs', 'Documentation'),
            ('/redoc', 'ReDoc')
        ]
        
        self.print_status("Test des endpoints API...", "INFO")
        results = {}
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f'http://localhost:8000{endpoint}', timeout=5)
                if response.status_code == 200:
                    self.print_status(f"✅ {name}: OK", "SUCCESS")
                    results[name] = True
                else:
                    self.print_status(f"⚠️ {name}: Code {response.status_code}", "WARNING")
                    results[name] = False
            except requests.exceptions.RequestException as e:
                self.print_status(f"❌ {name}: Erreur - {e}", "ERROR")
                results[name] = False
        
        self.test_results['api_endpoints'] = results
        return results

    def test_frontend_dependencies(self) -> bool:
        """Teste les dépendances frontend"""
        try:
            self.print_status("Test des dépendances frontend...", "INFO")
            
            frontend_path = Path("frontend")
            if not frontend_path.exists():
                self.print_status("Répertoire frontend non trouvé", "ERROR")
                return False
            
            # Test si node_modules existe
            node_modules = frontend_path / "node_modules"
            if node_modules.exists():
                self.print_status("Dépendances frontend installées", "SUCCESS")
                self.test_results['frontend_deps'] = True
                return True
            else:
                self.print_status("Dépendances frontend non installées", "WARNING")
                self.test_results['frontend_deps'] = False
                return False
                
        except Exception as e:
            self.print_status(f"Erreur test dépendances frontend: {e}", "ERROR")
            self.test_results['frontend_deps'] = False
            return False

    def generate_report(self):
        """Génère un rapport complet"""
        self.print_status("📊 === RAPPORT COMPLET ===", "INFO")
        
        # Backend
        backend_status = "✅ OK" if self.test_results.get('backend_import', False) else "❌ ERREUR"
        self.print_status(f"Backend Import: {backend_status}", "SUCCESS" if self.test_results.get('backend_import', False) else "ERROR")
        
        api_status = "✅ OK" if self.test_results.get('backend_api', False) else "❌ ERREUR"
        self.print_status(f"Backend API: {api_status}", "SUCCESS" if self.test_results.get('backend_api', False) else "ERROR")
        
        # Frontend
        frontend_status = "✅ OK" if self.test_results.get('frontend_config', False) else "❌ ERREUR"
        self.print_status(f"Frontend Config: {frontend_status}", "SUCCESS" if self.test_results.get('frontend_config', False) else "ERROR")
        
        deps_status = "✅ OK" if self.test_results.get('frontend_deps', False) else "⚠️ MANQUANT"
        self.print_status(f"Frontend Dependencies: {deps_status}", "SUCCESS" if self.test_results.get('frontend_deps', False) else "WARNING")
        
        # Infrastructure
        docker_status = "✅ OK" if self.test_results.get('docker', False) else "❌ MANQUANT"
        self.print_status(f"Docker: {docker_status}", "SUCCESS" if self.test_results.get('docker', False) else "ERROR")
        
        compose_status = "✅ OK" if self.test_results.get('docker_compose', False) else "❌ MANQUANT"
        self.print_status(f"Docker Compose: {compose_status}", "SUCCESS" if self.test_results.get('docker_compose', False) else "ERROR")
        
        makefile_status = "✅ OK" if self.test_results.get('makefile', False) else "❌ MANQUANT"
        self.print_status(f"Makefile: {makefile_status}", "SUCCESS" if self.test_results.get('makefile', False) else "ERROR")
        
        # API Endpoints
        if 'api_endpoints' in self.test_results:
            self.print_status("API Endpoints:", "INFO")
            for name, status in self.test_results['api_endpoints'].items():
                status_text = "✅ OK" if status else "❌ ERREUR"
                self.print_status(f"  {name}: {status_text}", "SUCCESS" if status else "ERROR")

    def cleanup(self):
        """Nettoie les processus"""
        self.print_status("Arrêt des processus...", "INFO")
        
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                self.print_status("Backend arrêté", "SUCCESS")
            except:
                self.backend_process.kill()
                self.print_status("Backend forcé à s'arrêter", "WARNING")
        
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
                self.print_status("Frontend arrêté", "SUCCESS")
            except:
                self.frontend_process.kill()
                self.print_status("Frontend forcé à s'arrêter", "WARNING")

    def signal_handler(self, signum, frame):
        """Gestionnaire de signaux pour arrêt propre"""
        self.print_status("Signal d'arrêt reçu...", "INFO")
        self.is_running = False
        self.cleanup()
        sys.exit(0)

    def run(self):
        """Fonction principale"""
        # Configuration des signaux
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.print_status("🚀 === LANCEMENT ROBUSTE BANKING TRANSFER PLATFORM ===", "INFO")
        self.print_status("Test et lancement de tous les composants...", "INFO")
        print()
        
        # Tests préliminaires
        self.print_status("🔍 Tests préliminaires...", "INFO")
        
        backend_ok = self.test_backend_import()
        frontend_ok = self.test_frontend_config()
        infra_ok = self.test_infrastructure()
        deps_ok = self.test_frontend_dependencies()
        
        print()
        
        if not backend_ok:
            self.print_status("❌ Backend non fonctionnel - Arrêt", "ERROR")
            return False
        
        # Lancement du backend
        self.print_status("🚀 Lancement de l'application...", "INFO")
        self.backend_process = self.launch_backend()
        
        if self.backend_process:
            print()
            # Test des endpoints
            self.test_api_endpoints()
            print()
            
            # Génération du rapport
            self.generate_report()
            print()
            
            # Instructions
            self.print_status("🎉 Application lancée avec succès!", "SUCCESS")
            self.print_status("📋 Endpoints disponibles sur http://localhost:8000", "INFO")
            self.print_status("📖 Documentation: http://localhost:8000/docs", "INFO")
            self.print_status("📊 ReDoc: http://localhost:8000/redoc", "INFO")
            print()
            self.print_status("Appuyez sur Ctrl+C pour arrêter l'application", "INFO")
            
            # Garde le processus en vie
            self.is_running = True
            try:
                while self.is_running:
                    time.sleep(1)
                    if self.backend_process.poll() is not None:
                        self.print_status("Backend s'est arrêté", "WARNING")
                        break
            except KeyboardInterrupt:
                self.print_status("Arrêt demandé par l'utilisateur", "INFO")
            finally:
                self.cleanup()
            
            return True
        else:
            self.print_status("❌ Impossible de lancer l'application", "ERROR")
            return False

def main():
    """Point d'entrée principal"""
    launcher = BankingTransferLauncher()
    success = launcher.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()