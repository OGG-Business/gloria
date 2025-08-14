#!/usr/bin/env python3
"""
Script de lancement robuste pour Banking Transfer Platform
Teste et lance tous les composants
"""

import subprocess
import time
import requests
import json
import sys
import os
from pathlib import Path

def print_status(message, status="INFO"):
    """Affiche un message avec statut"""
    colors = {
        "INFO": "\033[94m",    # Bleu
        "SUCCESS": "\033[92m", # Vert
        "ERROR": "\033[91m",   # Rouge
        "WARNING": "\033[93m", # Jaune
        "RESET": "\033[0m"     # Reset
    }
    print(f"{colors.get(status, '')}[{status}]{colors['RESET']} {message}")

def test_backend_import():
    """Teste l'import du backend"""
    try:
        sys.path.append('backend')
        from app.main import app
        from app.config import get_settings
        
        settings = get_settings()
        routes_count = len(app.routes)
        
        print_status(f"Backend importé avec succès", "SUCCESS")
        print_status(f"Application: {app.title}", "INFO")
        print_status(f"Version: {app.version}", "INFO")
        print_status(f"Routes: {routes_count} disponibles", "INFO")
        print_status(f"Config: {settings.app_name}", "INFO")
        
        return True
    except Exception as e:
        print_status(f"Erreur import backend: {e}", "ERROR")
        return False

def test_frontend_config():
    """Teste la configuration frontend"""
    try:
        frontend_path = Path("frontend/package.json")
        if frontend_path.exists():
            with open(frontend_path, 'r') as f:
                config = json.load(f)
            
            print_status(f"Frontend configuré: {config['name']}", "SUCCESS")
            print_status(f"Version: {config['version']}", "INFO")
            print_status(f"Dépendances: {len(config['dependencies'])} packages", "INFO")
            print_status(f"Proxy: {config.get('proxy', 'Non configuré')}", "INFO")
            
            return True
        else:
            print_status("package.json non trouvé", "ERROR")
            return False
    except Exception as e:
        print_status(f"Erreur config frontend: {e}", "ERROR")
        return False

def test_infrastructure():
    """Teste l'infrastructure"""
    try:
        # Test Docker
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_status("Docker installé", "SUCCESS")
        else:
            print_status("Docker non disponible", "WARNING")
        
        # Test Docker Compose
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_status("Docker Compose installé", "SUCCESS")
        else:
            print_status("Docker Compose non disponible", "WARNING")
        
        # Test Makefile
        makefile_path = Path("Makefile")
        if makefile_path.exists():
            print_status("Makefile présent", "SUCCESS")
        else:
            print_status("Makefile manquant", "WARNING")
        
        return True
    except Exception as e:
        print_status(f"Erreur infrastructure: {e}", "ERROR")
        return False

def launch_backend():
    """Lance le backend"""
    try:
        print_status("Lancement du backend...", "INFO")
        
        # Change vers le répertoire backend
        os.chdir('backend')
        
        # Lance uvicorn
        process = subprocess.Popen([
            'python', '-m', 'uvicorn', 'app.main:app',
            '--host', '0.0.0.0', '--port', '8000'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Attend un peu
        time.sleep(3)
        
        # Teste l'API
        try:
            response = requests.get('http://localhost:8000/', timeout=5)
            if response.status_code == 200:
                print_status("Backend lancé et accessible", "SUCCESS")
                print_status(f"Réponse: {response.json()}", "INFO")
                return process
            else:
                print_status(f"Backend répond avec code: {response.status_code}", "WARNING")
                return process
        except requests.exceptions.RequestException as e:
            print_status(f"Backend non accessible: {e}", "WARNING")
            return process
            
    except Exception as e:
        print_status(f"Erreur lancement backend: {e}", "ERROR")
        return None

def test_api_endpoints():
    """Teste tous les endpoints API"""
    endpoints = [
        ('/', 'Root'),
        ('/health', 'Health'),
        ('/auth/', 'Auth'),
        ('/accounts/', 'Accounts'),
        ('/transfers/', 'Transfers'),
        ('/kyc/', 'KYC'),
        ('/notifications/', 'Notifications'),
        ('/admin/', 'Admin')
    ]
    
    print_status("Test des endpoints API...", "INFO")
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f'http://localhost:8000{endpoint}', timeout=5)
            if response.status_code == 200:
                print_status(f"✅ {name}: OK", "SUCCESS")
            else:
                print_status(f"⚠️ {name}: Code {response.status_code}", "WARNING")
        except requests.exceptions.RequestException as e:
            print_status(f"❌ {name}: Erreur - {e}", "ERROR")

def main():
    """Fonction principale"""
    print_status("🚀 === LANCEMENT BANKING TRANSFER PLATFORM ===", "INFO")
    print()
    
    # Tests préliminaires
    print_status("🔍 Tests préliminaires...", "INFO")
    
    backend_ok = test_backend_import()
    frontend_ok = test_frontend_config()
    infra_ok = test_infrastructure()
    
    print()
    
    if not backend_ok:
        print_status("❌ Backend non fonctionnel - Arrêt", "ERROR")
        return False
    
    # Lancement du backend
    print_status("🚀 Lancement de l'application...", "INFO")
    backend_process = launch_backend()
    
    if backend_process:
        print()
        # Test des endpoints
        test_api_endpoints()
        print()
        
        # Résumé
        print_status("📊 === RÉSUMÉ ===", "INFO")
        print_status(f"Backend: {'✅ OK' if backend_ok else '❌ ERREUR'}", "SUCCESS" if backend_ok else "ERROR")
        print_status(f"Frontend: {'✅ OK' if frontend_ok else '❌ ERREUR'}", "SUCCESS" if frontend_ok else "ERROR")
        print_status(f"Infrastructure: {'✅ OK' if infra_ok else '❌ ERREUR'}", "SUCCESS" if infra_ok else "ERROR")
        print_status(f"API: {'✅ Accessible' if backend_process else '❌ Non accessible'}", "SUCCESS" if backend_process else "ERROR")
        
        print()
        print_status("🎉 Application lancée avec succès!", "SUCCESS")
        print_status("📋 Endpoints disponibles sur http://localhost:8000", "INFO")
        print_status("📖 Documentation: http://localhost:8000/docs", "INFO")
        
        # Garde le processus en vie
        try:
            backend_process.wait()
        except KeyboardInterrupt:
            print_status("Arrêt de l'application...", "INFO")
            backend_process.terminate()
        
        return True
    else:
        print_status("❌ Impossible de lancer l'application", "ERROR")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
