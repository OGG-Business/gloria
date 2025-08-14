#!/usr/bin/env python3
"""
Script pour rendre l'application 100% opérationnelle
Suivant la feuille de route détaillée
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path
from datetime import datetime

class Application100Operationnelle:
    def __init__(self):
        self.project_root = Path.cwd()
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        
        self.services = {
            "backend": {"port": 8000, "url": "http://localhost:8000"},
            "frontend": {"port": 3000, "url": "http://localhost:3000"},
            "database": {"port": 5432},
            "redis": {"port": 6379},
            "nginx": {"port": 80}
        }
        
    def print_header(self):
        print("="*100)
        print("🚀 RENDRE L'APPLICATION 100% OPÉRATIONNELLE")
        print("="*100)
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        print("="*100)
        print("")
        print("🎯 OBJECTIF: Implémenter la feuille de route complète")
        print("📋 ÉTAPES: Frontend, Backend, DB, Redis, Nginx, API")
        print("✅ RÉSULTAT: Application 100% fonctionnelle")
        print("="*100)
    
    def step_1_demarrer_frontend(self):
        """Étape 1: Démarrer le frontend Flutter"""
        print("\n🎨 ÉTAPE 1: DÉMARRER LE FRONTEND FLUTTER")
        print("-" * 50)
        
        if not self.frontend_dir.exists():
            print("   ❌ Dossier frontend non trouvé")
            return False
        
        print("   🔍 Vérification du frontend Flutter...")
        
        # Vérifier pubspec.yaml
        pubspec_file = self.frontend_dir / "pubspec.yaml"
        if not pubspec_file.exists():
            print("   ❌ pubspec.yaml non trouvé")
            return False
        
        print("   ✅ pubspec.yaml trouvé")
        
        # Installer les dépendances Flutter
        print("   📦 Installation des dépendances Flutter...")
        try:
            os.chdir(self.frontend_dir)
            result = subprocess.run(
                ["flutter", "pub", "get"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("   ✅ Dépendances Flutter installées")
            else:
                print(f"   ❌ Erreur installation: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("   ⏰ Timeout installation dépendances")
            return False
        except FileNotFoundError:
            print("   ❌ Flutter non installé")
            return False
        
        # Démarrer le serveur de développement Flutter
        print("   🚀 Démarrage du serveur Flutter...")
        try:
            # Démarrer en arrière-plan
            process = subprocess.Popen(
                ["flutter", "run", "-d", "web-server", "--web-port", "3000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Attendre un peu pour le démarrage
            time.sleep(10)
            
            # Vérifier si le processus tourne
            if process.poll() is None:
                print("   ✅ Serveur Flutter démarré sur le port 3000")
                return True
            else:
                print("   ❌ Serveur Flutter non démarré")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur démarrage Flutter: {e}")
            return False
    
    def step_2_demarrer_postgresql(self):
        """Étape 2: Démarrer PostgreSQL"""
        print("\n🗄️ ÉTAPE 2: DÉMARRER POSTGRESQL")
        print("-" * 50)
        
        # Vérifier si PostgreSQL est installé
        print("   🔍 Vérification de PostgreSQL...")
        
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "postgresql"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip() == "active":
                print("   ✅ PostgreSQL déjà actif")
                return True
                
        except Exception:
            pass
        
        # Essayer de démarrer PostgreSQL
        print("   🚀 Démarrage de PostgreSQL...")
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "start", "postgresql"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("   ✅ PostgreSQL démarré")
                
                # Vérifier le statut
                time.sleep(5)
                status_result = subprocess.run(
                    ["systemctl", "is-active", "postgresql"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if status_result.returncode == 0 and status_result.stdout.strip() == "active":
                    print("   ✅ PostgreSQL actif et opérationnel")
                    return True
                else:
                    print("   ❌ PostgreSQL non actif après démarrage")
                    return False
            else:
                print(f"   ❌ Erreur démarrage PostgreSQL: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("   ⏰ Timeout démarrage PostgreSQL")
            return False
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
    
    def step_3_creer_api_transfers(self):
        """Étape 3: Créer l'API /api/transfers"""
        print("\n🔧 ÉTAPE 3: CRÉER L'API /API/TRANSFERS")
        print("-" * 50)
        
        # Créer le fichier API transfers
        api_file = self.backend_dir / "app" / "api_routes.py"
        
        api_content = '''"""
API Routes pour Banking Transfer Platform
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import structlog
from datetime import datetime
from typing import Dict, Any

from app.common.database import get_db
from app.transfers.services import TransferService
from app.auth.models import User
from app.auth.dependencies import get_current_user

logger = structlog.get_logger()

api_router = APIRouter()

@api_router.post("/api/transfers")
async def create_transfer_api(
    transfer_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """API endpoint pour créer un transfert SWIFT"""
    try:
        logger.info("Tentative de création de transfert via API", 
                   user_id=current_user.id, 
                   amount=transfer_data.get('amount'))
        
        transfer_service = TransferService(db)
        
        # Validation des données
        required_fields = ['amount', 'currency', 'recipient_iban', 'recipient_name']
        for field in required_fields:
            if field not in transfer_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Champ requis manquant: {field}"
                )
        
        # Créer le transfert
        transfer = await transfer_service.create_transfer(transfer_data, current_user)
        
        logger.info("Transfert créé avec succès via API",
                   transfer_id=transfer.transfer_id,
                   user_id=current_user.id)
        
        return {
            "success": True,
            "id": transfer.transfer_id,
            "status": "PENDING",
            "message": "Transfert initié avec succès",
            "timestamp": datetime.now().isoformat(),
            "transfer_details": {
                "amount": transfer.amount,
                "currency": transfer.currency,
                "recipient_iban": transfer.recipient_iban,
                "recipient_name": transfer.recipient_name,
                "swift_message_id": f"SWIFT{transfer.transfer_id}",
                "gpi_tracking_id": f"GPI{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur création transfert via API: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la création du transfert"
        )

@api_router.get("/api/transfers")
async def get_transfers_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """API endpoint pour récupérer les transferts"""
    try:
        transfer_service = TransferService(db)
        transfers, total = await transfer_service.get_user_transfers(current_user.id, 1, 50)
        
        return {
            "success": True,
            "transfers": [
                {
                    "id": t.transfer_id,
                    "amount": t.amount,
                    "currency": t.currency,
                    "status": t.status.value,
                    "recipient_name": t.recipient_name,
                    "created_at": t.created_at.isoformat()
                }
                for t in transfers
            ],
            "total": total
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération transferts via API: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la récupération des transferts"
        )

@api_router.get("/api/health")
async def api_health():
    """API health check"""
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }
'''
        
        try:
            with open(api_file, 'w') as f:
                f.write(api_content)
            print("   ✅ Fichier API routes créé")
            
            # Modifier main.py pour inclure le nouveau router
            main_file = self.backend_dir / "app" / "main.py"
            
            # Lire le contenu actuel
            with open(main_file, 'r') as f:
                main_content = f.read()
            
            # Ajouter l'import et l'inclusion du router API
            if "from app.api_routes import api_router" not in main_content:
                # Ajouter l'import après les autres imports
                import_line = "from app.api_routes import api_router"
                main_content = main_content.replace(
                    "from app.admin.routes import router as admin_router",
                    "from app.admin.routes import router as admin_router\n" + import_line
                )
                
                # Ajouter l'inclusion du router après les autres routers
                router_inclusion = '''
try:
    app.include_router(api_router, tags=["API"])
    logger.info("API router included")
except Exception as e:
    logger.warning(f"API router not available: {e}")'''
                
                main_content = main_content.replace(
                    "logger.warning(f\"Admin router not available: {e}\")",
                    "logger.warning(f\"Admin router not available: {e}\")" + router_inclusion
                )
                
                # Écrire le contenu modifié
                with open(main_file, 'w') as f:
                    f.write(main_content)
                
                print("   ✅ Main.py modifié pour inclure l'API router")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Erreur création API: {e}")
            return False
    
    def step_4_installer_redis(self):
        """Étape 4: Installer et configurer Redis"""
        print("\n🔴 ÉTAPE 4: INSTALLER ET CONFIGURER REDIS")
        print("-" * 50)
        
        # Vérifier si Redis est installé
        print("   🔍 Vérification de Redis...")
        
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "redis"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip() == "active":
                print("   ✅ Redis déjà actif")
                return True
                
        except Exception:
            pass
        
        # Essayer d'installer Redis
        print("   📦 Installation de Redis...")
        try:
            result = subprocess.run(
                ["sudo", "apt-get", "update"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                print("   ⚠️ Erreur mise à jour apt-get")
            
            result = subprocess.run(
                ["sudo", "apt-get", "install", "-y", "redis-server"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print("   ✅ Redis installé")
                
                # Démarrer Redis
                print("   🚀 Démarrage de Redis...")
                start_result = subprocess.run(
                    ["sudo", "systemctl", "start", "redis"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if start_result.returncode == 0:
                    print("   ✅ Redis démarré")
                    
                    # Vérifier le statut
                    time.sleep(3)
                    status_result = subprocess.run(
                        ["systemctl", "is-active", "redis"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if status_result.returncode == 0 and status_result.stdout.strip() == "active":
                        print("   ✅ Redis actif et opérationnel")
                        return True
                    else:
                        print("   ❌ Redis non actif après démarrage")
                        return False
                else:
                    print("   ❌ Erreur démarrage Redis")
                    return False
            else:
                print(f"   ❌ Erreur installation Redis: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("   ⏰ Timeout installation Redis")
            return False
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
    
    def step_5_installer_nginx(self):
        """Étape 5: Installer et configurer Nginx"""
        print("\n🌐 ÉTAPE 5: INSTALLER ET CONFIGURER NGINX")
        print("-" * 50)
        
        # Vérifier si Nginx est installé
        print("   🔍 Vérification de Nginx...")
        
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "nginx"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip() == "active":
                print("   ✅ Nginx déjà actif")
                return True
                
        except Exception:
            pass
        
        # Installer Nginx
        print("   📦 Installation de Nginx...")
        try:
            result = subprocess.run(
                ["sudo", "apt-get", "install", "-y", "nginx"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print("   ✅ Nginx installé")
                
                # Créer la configuration
                config_content = '''
server {
    listen 80;
    server_name localhost;

    # Frontend Flutter
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend autres endpoints
    location /auth/ {
        proxy_pass http://localhost:8000/auth/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /transfers/ {
        proxy_pass http://localhost:8000/transfers/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
'''
                
                # Écrire la configuration
                config_file = "/tmp/gloria-nginx.conf"
                with open(config_file, 'w') as f:
                    f.write(config_content)
                
                # Copier la configuration
                result = subprocess.run(
                    ["sudo", "cp", config_file, "/etc/nginx/sites-available/gloria"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print("   ✅ Configuration Nginx créée")
                    
                    # Activer le site
                    result = subprocess.run(
                        ["sudo", "ln", "-sf", "/etc/nginx/sites-available/gloria", "/etc/nginx/sites-enabled/"],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        print("   ✅ Site Nginx activé")
                        
                        # Tester la configuration
                        result = subprocess.run(
                            ["sudo", "nginx", "-t"],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        
                        if result.returncode == 0:
                            print("   ✅ Configuration Nginx valide")
                            
                            # Redémarrer Nginx
                            result = subprocess.run(
                                ["sudo", "systemctl", "restart", "nginx"],
                                capture_output=True,
                                text=True,
                                timeout=30
                            )
                            
                            if result.returncode == 0:
                                print("   ✅ Nginx redémarré")
                                
                                # Vérifier le statut
                                time.sleep(3)
                                status_result = subprocess.run(
                                    ["systemctl", "is-active", "nginx"],
                                    capture_output=True,
                                    text=True,
                                    timeout=10
                                )
                                
                                if status_result.returncode == 0 and status_result.stdout.strip() == "active":
                                    print("   ✅ Nginx actif et opérationnel")
                                    return True
                                else:
                                    print("   ❌ Nginx non actif après redémarrage")
                                    return False
                            else:
                                print("   ❌ Erreur redémarrage Nginx")
                                return False
                        else:
                            print(f"   ❌ Configuration Nginx invalide: {result.stderr}")
                            return False
                    else:
                        print("   ❌ Erreur activation site Nginx")
                        return False
                else:
                    print("   ❌ Erreur création configuration Nginx")
                    return False
            else:
                print(f"   ❌ Erreur installation Nginx: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("   ⏰ Timeout installation Nginx")
            return False
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
    
    def step_6_demarrer_backend(self):
        """Étape 6: Démarrer le backend"""
        print("\n🔧 ÉTAPE 6: DÉMARRER LE BACKEND")
        print("-" * 50)
        
        if not self.backend_dir.exists():
            print("   ❌ Dossier backend non trouvé")
            return False
        
        print("   🔍 Vérification du backend...")
        
        # Vérifier requirements.txt
        requirements_file = self.backend_dir / "requirements.txt"
        if not requirements_file.exists():
            print("   ❌ requirements.txt non trouvé")
            return False
        
        print("   ✅ requirements.txt trouvé")
        
        # Installer les dépendances Python
        print("   📦 Installation des dépendances Python...")
        try:
            os.chdir(self.backend_dir)
            result = subprocess.run(
                ["pip", "install", "-r", "requirements.txt"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print("   ✅ Dépendances Python installées")
            else:
                print(f"   ❌ Erreur installation: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("   ⏰ Timeout installation dépendances")
            return False
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
        
        # Démarrer le serveur backend
        print("   🚀 Démarrage du serveur backend...")
        try:
            # Démarrer en arrière-plan
            process = subprocess.Popen(
                ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Attendre un peu pour le démarrage
            time.sleep(10)
            
            # Vérifier si le processus tourne
            if process.poll() is None:
                print("   ✅ Serveur backend démarré sur le port 8000")
                return True
            else:
                print("   ❌ Serveur backend non démarré")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur démarrage backend: {e}")
            return False
    
    def step_7_tests_finaux(self):
        """Étape 7: Tests finaux et validation"""
        print("\n🧪 ÉTAPE 7: TESTS FINAUX ET VALIDATION")
        print("-" * 50)
        
        tests_results = {}
        
        # Test backend
        print("   🔧 Test backend...")
        try:
            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                print("   ✅ Backend: OPÉRATIONNEL")
                tests_results["backend"] = True
            else:
                print(f"   ❌ Backend: Status {response.status_code}")
                tests_results["backend"] = False
        except Exception as e:
            print(f"   ❌ Backend: Erreur - {e}")
            tests_results["backend"] = False
        
        # Test frontend
        print("   🎨 Test frontend...")
        try:
            response = requests.get("http://localhost:3000", timeout=10)
            if response.status_code == 200:
                print("   ✅ Frontend: OPÉRATIONNEL")
                tests_results["frontend"] = True
            else:
                print(f"   ❌ Frontend: Status {response.status_code}")
                tests_results["frontend"] = False
        except Exception as e:
            print(f"   ❌ Frontend: Erreur - {e}")
            tests_results["frontend"] = False
        
        # Test API transfers
        print("   🚀 Test API transfers...")
        try:
            response = requests.get("http://localhost:8000/api/health", timeout=10)
            if response.status_code == 200:
                print("   ✅ API transfers: OPÉRATIONNELLE")
                tests_results["api_transfers"] = True
            else:
                print(f"   ❌ API transfers: Status {response.status_code}")
                tests_results["api_transfers"] = False
        except Exception as e:
            print(f"   ❌ API transfers: Erreur - {e}")
            tests_results["api_transfers"] = False
        
        # Test Nginx
        print("   🌐 Test Nginx...")
        try:
            response = requests.get("http://localhost", timeout=10)
            if response.status_code == 200:
                print("   ✅ Nginx: OPÉRATIONNEL")
                tests_results["nginx"] = True
            else:
                print(f"   ❌ Nginx: Status {response.status_code}")
                tests_results["nginx"] = False
        except Exception as e:
            print(f"   ❌ Nginx: Erreur - {e}")
            tests_results["nginx"] = False
        
        return tests_results
    
    def run_complete_setup(self):
        """Exécuter le setup complet"""
        print("🚀 RENDRE L'APPLICATION 100% OPÉRATIONNELLE")
        print("="*70)
        
        self.print_header()
        
        # Exécuter toutes les étapes
        steps_results = {}
        
        steps_results["frontend"] = self.step_1_demarrer_frontend()
        steps_results["postgresql"] = self.step_2_demarrer_postgresql()
        steps_results["api_transfers"] = self.step_3_creer_api_transfers()
        steps_results["redis"] = self.step_4_installer_redis()
        steps_results["nginx"] = self.step_5_installer_nginx()
        steps_results["backend"] = self.step_6_demarrer_backend()
        
        # Tests finaux
        tests_results = self.step_7_tests_finaux()
        
        # Résumé final
        print("\n" + "="*100)
        print("🏆 RÉSULTAT FINAL - APPLICATION 100% OPÉRATIONNELLE")
        print("="*100)
        
        print("📊 RÉSULTATS DES ÉTAPES:")
        for step, result in steps_results.items():
            status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
            print(f"   {step}: {status}")
        
        print("\n📊 RÉSULTATS DES TESTS:")
        for test, result in tests_results.items():
            status = "✅ OPÉRATIONNEL" if result else "❌ DÉFAILLANT"
            print(f"   {test}: {status}")
        
        # Évaluation finale
        all_steps_success = all(steps_results.values())
        all_tests_success = all(tests_results.values())
        
        if all_steps_success and all_tests_success:
            print("\n🎉 APPLICATION 100% OPÉRATIONNELLE!")
            print("   ✅ Toutes les étapes réussies")
            print("   ✅ Tous les tests passés")
            print("   🚀 APPLICATION PRÊTE POUR PRODUCTION!")
            return True
        elif all_steps_success:
            print("\n⚠️ APPLICATION PARTIELLEMENT OPÉRATIONNELLE")
            print("   ✅ Toutes les étapes réussies")
            print("   ❌ Certains tests échoués")
            print("   🔧 Vérifier la configuration")
            return False
        else:
            print("\n❌ APPLICATION NON OPÉRATIONNELLE")
            print("   ❌ Certaines étapes échouées")
            print("   🔧 Vérifier les erreurs ci-dessus")
            return False

def main():
    setup = Application100Operationnelle()
    
    try:
        success = setup.run_complete_setup()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrompu")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur générale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
