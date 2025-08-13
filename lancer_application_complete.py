#!/usr/bin/env python3
"""
Lancer Application Complète - Services Manquants
Script pour lancer tous les services manquants et tester la connexion complète
"""

import subprocess
import time
import os
from datetime import datetime

def lancer_application_complete():
    print("🚀 LANCEMENT APPLICATION COMPLÈTE - SERVICES MANQUANTS")
    print("="*80)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("="*80)
    
    results = {}
    
    # 1. Vérification et lancement PostgreSQL
    print("\n🗄️ 1. Base de Données PostgreSQL")
    print("-" * 50)
    
    try:
        # Vérifier si PostgreSQL est installé
        pg_version = subprocess.run(['psql', '--version'], 
                                  capture_output=True, text=True, timeout=10)
        if pg_version.returncode == 0:
            print("   ✅ PostgreSQL: INSTALLÉ")
            print(f"   📋 Version: {pg_version.stdout.strip()}")
            
            # Tenter de démarrer PostgreSQL
            print("   🔧 Tentative de démarrage PostgreSQL...")
            try:
                pg_start = subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'], 
                                        capture_output=True, text=True, timeout=30)
                if pg_start.returncode == 0:
                    print("   ✅ PostgreSQL: DÉMARRÉ")
                    results['postgresql'] = "DÉMARRÉ"
                else:
                    print("   ❌ PostgreSQL: ÉCHEC DÉMARRAGE")
                    print("   📝 Erreur:", pg_start.stderr)
                    results['postgresql'] = "ÉCHEC DÉMARRAGE"
            except Exception as e:
                print(f"   ❌ Erreur démarrage PostgreSQL: {e}")
                results['postgresql'] = f"ERREUR: {e}"
        else:
            print("   ❌ PostgreSQL: NON INSTALLÉ")
            print("   🔧 Installation PostgreSQL...")
            try:
                pg_install = subprocess.run(['sudo', 'apt-get', 'update'], 
                                          capture_output=True, text=True, timeout=60)
                pg_install = subprocess.run(['sudo', 'apt-get', 'install', '-y', 'postgresql', 'postgresql-contrib'], 
                                          capture_output=True, text=True, timeout=300)
                if pg_install.returncode == 0:
                    print("   ✅ PostgreSQL: INSTALLÉ")
                    results['postgresql'] = "INSTALLÉ"
                else:
                    print("   ❌ PostgreSQL: ÉCHEC INSTALLATION")
                    results['postgresql'] = "ÉCHEC INSTALLATION"
            except Exception as e:
                print(f"   ❌ Erreur installation PostgreSQL: {e}")
                results['postgresql'] = f"ERREUR: {e}"
    except Exception as e:
        print(f"   ❌ Erreur PostgreSQL: {e}")
        results['postgresql'] = f"ERREUR: {e}"
    
    # 2. Vérification et lancement Redis
    print("\n🔴 2. Cache Redis")
    print("-" * 50)
    
    try:
        # Vérifier si Redis est installé
        redis_version = subprocess.run(['redis-server', '--version'], 
                                     capture_output=True, text=True, timeout=10)
        if redis_version.returncode == 0:
            print("   ✅ Redis: INSTALLÉ")
            print(f"   📋 Version: {redis_version.stdout.strip()}")
            
            # Tenter de démarrer Redis
            print("   🔧 Tentative de démarrage Redis...")
            try:
                redis_start = subprocess.run(['sudo', 'systemctl', 'start', 'redis-server'], 
                                           capture_output=True, text=True, timeout=30)
                if redis_start.returncode == 0:
                    print("   ✅ Redis: DÉMARRÉ")
                    results['redis'] = "DÉMARRÉ"
                else:
                    print("   ❌ Redis: ÉCHEC DÉMARRAGE")
                    print("   📝 Erreur:", redis_start.stderr)
                    results['redis'] = "ÉCHEC DÉMARRAGE"
            except Exception as e:
                print(f"   ❌ Erreur démarrage Redis: {e}")
                results['redis'] = f"ERREUR: {e}"
        else:
            print("   ❌ Redis: NON INSTALLÉ")
            print("   🔧 Installation Redis...")
            try:
                redis_install = subprocess.run(['sudo', 'apt-get', 'install', '-y', 'redis-server'], 
                                             capture_output=True, text=True, timeout=300)
                if redis_install.returncode == 0:
                    print("   ✅ Redis: INSTALLÉ")
                    results['redis'] = "INSTALLÉ"
                else:
                    print("   ❌ Redis: ÉCHEC INSTALLATION")
                    results['redis'] = "ÉCHEC INSTALLATION"
            except Exception as e:
                print(f"   ❌ Erreur installation Redis: {e}")
                results['redis'] = f"ERREUR: {e}"
    except Exception as e:
        print(f"   ❌ Erreur Redis: {e}")
        results['redis'] = f"ERREUR: {e}"
    
    # 3. Vérification et lancement Nginx
    print("\n🌐 3. Serveur Web Nginx")
    print("-" * 50)
    
    try:
        # Vérifier si Nginx est installé
        nginx_version = subprocess.run(['nginx', '-v'], 
                                     capture_output=True, text=True, timeout=10)
        if nginx_version.returncode == 0:
            print("   ✅ Nginx: INSTALLÉ")
            print(f"   📋 Version: {nginx_version.stderr.strip()}")
            
            # Tenter de démarrer Nginx
            print("   🔧 Tentative de démarrage Nginx...")
            try:
                nginx_start = subprocess.run(['sudo', 'systemctl', 'start', 'nginx'], 
                                           capture_output=True, text=True, timeout=30)
                if nginx_start.returncode == 0:
                    print("   ✅ Nginx: DÉMARRÉ")
                    results['nginx'] = "DÉMARRÉ"
                else:
                    print("   ❌ Nginx: ÉCHEC DÉMARRAGE")
                    print("   📝 Erreur:", nginx_start.stderr)
                    results['nginx'] = "ÉCHEC DÉMARRAGE"
            except Exception as e:
                print(f"   ❌ Erreur démarrage Nginx: {e}")
                results['nginx'] = f"ERREUR: {e}"
        else:
            print("   ❌ Nginx: NON INSTALLÉ")
            print("   🔧 Installation Nginx...")
            try:
                nginx_install = subprocess.run(['sudo', 'apt-get', 'install', '-y', 'nginx'], 
                                             capture_output=True, text=True, timeout=300)
                if nginx_install.returncode == 0:
                    print("   ✅ Nginx: INSTALLÉ")
                    results['nginx'] = "INSTALLÉ"
                else:
                    print("   ❌ Nginx: ÉCHEC INSTALLATION")
                    results['nginx'] = "ÉCHEC INSTALLATION"
            except Exception as e:
                print(f"   ❌ Erreur installation Nginx: {e}")
                results['nginx'] = f"ERREUR: {e}"
    except Exception as e:
        print(f"   ❌ Erreur Nginx: {e}")
        results['nginx'] = f"ERREUR: {e}"
    
    # 4. Vérification et lancement Frontend Flutter
    print("\n📱 4. Frontend Flutter")
    print("-" * 50)
    
    try:
        # Vérifier si Flutter est installé
        flutter_version = subprocess.run(['flutter', '--version'], 
                                       capture_output=True, text=True, timeout=10)
        if flutter_version.returncode == 0:
            print("   ✅ Flutter: INSTALLÉ")
            print("   📋 Version détectée")
            
            # Vérifier le projet Flutter
            if os.path.exists('frontend'):
                print("   ✅ Projet Flutter: PRÉSENT")
                
                # Tenter de lancer Flutter
                print("   🔧 Tentative de lancement Flutter...")
                try:
                    os.chdir('frontend')
                    flutter_run = subprocess.run(['flutter', 'run', '--web-port', '3000'], 
                                               capture_output=True, text=True, timeout=60)
                    if flutter_run.returncode == 0:
                        print("   ✅ Frontend Flutter: DÉMARRÉ")
                        results['frontend'] = "DÉMARRÉ"
                    else:
                        print("   ⚠️ Frontend Flutter: ERREUR DÉMARRAGE")
                        print("   📝 Erreur:", flutter_run.stderr)
                        results['frontend'] = "ERREUR DÉMARRAGE"
                except Exception as e:
                    print(f"   ❌ Erreur lancement Flutter: {e}")
                    results['frontend'] = f"ERREUR: {e}"
                finally:
                    os.chdir('..')
            else:
                print("   ❌ Projet Flutter: MANQUANT")
                print("   🔧 Création projet Flutter...")
                try:
                    flutter_create = subprocess.run(['flutter', 'create', 'frontend'], 
                                                  capture_output=True, text=True, timeout=300)
                    if flutter_create.returncode == 0:
                        print("   ✅ Projet Flutter: CRÉÉ")
                        results['frontend'] = "CRÉÉ"
                    else:
                        print("   ❌ Projet Flutter: ÉCHEC CRÉATION")
                        results['frontend'] = "ÉCHEC CRÉATION"
                except Exception as e:
                    print(f"   ❌ Erreur création Flutter: {e}")
                    results['frontend'] = f"ERREUR: {e}"
        else:
            print("   ❌ Flutter: NON INSTALLÉ")
            print("   🔧 Installation Flutter...")
            try:
                # Installation Flutter
                flutter_install = subprocess.run(['curl', '-o', 'flutter.tar.xz', 'https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.19.6-stable.tar.xz'], 
                                               capture_output=True, text=True, timeout=300)
                if flutter_install.returncode == 0:
                    subprocess.run(['tar', 'xf', 'flutter.tar.xz'], 
                                 capture_output=True, text=True, timeout=300)
                    subprocess.run(['export', 'PATH="$PATH:`pwd`/flutter/bin"'], 
                                 shell=True, capture_output=True, text=True, timeout=10)
                    print("   ✅ Flutter: INSTALLÉ")
                    results['frontend'] = "INSTALLÉ"
                else:
                    print("   ❌ Flutter: ÉCHEC INSTALLATION")
                    results['frontend'] = "ÉCHEC INSTALLATION"
            except Exception as e:
                print(f"   ❌ Erreur installation Flutter: {e}")
                results['frontend'] = f"ERREUR: {e}"
    except Exception as e:
        print(f"   ❌ Erreur Flutter: {e}")
        results['frontend'] = f"ERREUR: {e}"
    
    # 5. Test final de l'application complète
    print("\n🏆 5. Test Final Application Complète")
    print("-" * 50)
    
    try:
        # Importer et exécuter le test complet
        import test_connexion_application_complete
        final_results = test_connexion_application_complete.test_connexion_application_complete()
        
        print("\n📊 RÉSULTAT FINAL:")
        print(f"   🔧 Backend: {final_results.get('backend', 'N/A')}")
        print(f"   📱 Frontend: {final_results.get('frontend', 'N/A')}")
        print(f"   🗄️ PostgreSQL: {final_results.get('postgresql', 'N/A')}")
        print(f"   🔴 Redis: {final_results.get('redis', 'N/A')}")
        print(f"   🌐 Nginx: {final_results.get('nginx', 'N/A')}")
        print(f"   🚀 API: {final_results.get('api_backend', 'N/A')}")
        print(f"   💸 SWIFT: {final_results.get('transfert_swift', 'N/A')}")
        
        if final_results.get('final_status') == "SUCCÈS_APPLICATION_RÉELLE":
            print("\n🎉 SUCCÈS: APPLICATION COMPLÈTE 100% RÉELLE!")
            results['final_status'] = "SUCCÈS_COMPLET"
        else:
            print("\n⚠️ APPLICATION PARTIELLEMENT OPÉRATIONNELLE")
            results['final_status'] = "PARTIEL"
            
    except Exception as e:
        print(f"   ❌ Erreur test final: {e}")
        results['final_status'] = f"ERREUR: {e}"
    
    return results

if __name__ == "__main__":
    try:
        print("🚀 Démarrage du lancement application complète...")
        results = lancer_application_complete()
        
        print(f"\n📋 Status Final: {results.get('final_status', 'N/A')}")
        
        if results.get('final_status') == "SUCCÈS_COMPLET":
            print("\n🎉 FÉLICITATIONS! L'application complète est 100% RÉELLE!")
        else:
            print("\n⚠️ L'application est partiellement opérationnelle.")
            
    except Exception as e:
        print(f"\n❌ ERREUR GÉNÉRALE: {e}")