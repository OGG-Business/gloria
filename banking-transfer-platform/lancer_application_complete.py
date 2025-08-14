#!/usr/bin/env python3
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
    
    print("\n🗄️ 1. Base de Données PostgreSQL")
    print("-" * 50)
    
    try:
        pg_version = subprocess.run(['psql', '--version'], 
                                  capture_output=True, text=True, timeout=10)
        if pg_version.returncode == 0:
            print("   ✅ PostgreSQL: INSTALLÉ")
            print(f"   📋 Version: {pg_version.stdout.strip()}")
            
            print("   🔧 Tentative de démarrage PostgreSQL...")
            try:
                pg_start = subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'], 
                                        capture_output=True, text=True, timeout=30)
                if pg_start.returncode == 0:
                    print("   ✅ PostgreSQL: DÉMARRÉ")
                    results['postgresql'] = "DÉMARRÉ"
                else:
                    print("   ❌ PostgreSQL: ÉCHEC DÉMARRAGE")
                    results['postgresql'] = "ÉCHEC DÉMARRAGE"
            except Exception as e:
                print(f"   ❌ Erreur démarrage PostgreSQL: {e}")
                results['postgresql'] = f"ERREUR: {e}"
        else:
            print("   ❌ PostgreSQL: NON INSTALLÉ")
            results['postgresql'] = "NON INSTALLÉ"
    except Exception as e:
        print(f"   ❌ Erreur PostgreSQL: {e}")
        results['postgresql'] = f"ERREUR: {e}"
    
    print("\n🔴 2. Cache Redis")
    print("-" * 50)
    
    try:
        redis_version = subprocess.run(['redis-server', '--version'], 
                                     capture_output=True, text=True, timeout=10)
        if redis_version.returncode == 0:
            print("   ✅ Redis: INSTALLÉ")
            print(f"   📋 Version: {redis_version.stdout.strip()}")
            
            print("   🔧 Tentative de démarrage Redis...")
            try:
                redis_start = subprocess.run(['sudo', 'systemctl', 'start', 'redis-server'], 
                                           capture_output=True, text=True, timeout=30)
                if redis_start.returncode == 0:
                    print("   ✅ Redis: DÉMARRÉ")
                    results['redis'] = "DÉMARRÉ"
                else:
                    print("   ❌ Redis: ÉCHEC DÉMARRAGE")
                    results['redis'] = "ÉCHEC DÉMARRAGE"
            except Exception as e:
                print(f"   ❌ Erreur démarrage Redis: {e}")
                results['redis'] = f"ERREUR: {e}"
        else:
            print("   ❌ Redis: NON INSTALLÉ")
            results['redis'] = "NON INSTALLÉ"
    except Exception as e:
        print(f"   ❌ Erreur Redis: {e}")
        results['redis'] = f"ERREUR: {e}"
    
    print("\n🌐 3. Serveur Web Nginx")
    print("-" * 50)
    
    try:
        nginx_version = subprocess.run(['nginx', '-v'], 
                                     capture_output=True, text=True, timeout=10)
        if nginx_version.returncode == 0:
            print("   ✅ Nginx: INSTALLÉ")
            print(f"   📋 Version: {nginx_version.stderr.strip()}")
            
            print("   🔧 Tentative de démarrage Nginx...")
            try:
                nginx_start = subprocess.run(['sudo', 'systemctl', 'start', 'nginx'], 
                                           capture_output=True, text=True, timeout=30)
                if nginx_start.returncode == 0:
                    print("   ✅ Nginx: DÉMARRÉ")
                    results['nginx'] = "DÉMARRÉ"
                else:
                    print("   ❌ Nginx: ÉCHEC DÉMARRAGE")
                    results['nginx'] = "ÉCHEC DÉMARRAGE"
            except Exception as e:
                print(f"   ❌ Erreur démarrage Nginx: {e}")
                results['nginx'] = f"ERREUR: {e}"
        else:
            print("   ❌ Nginx: NON INSTALLÉ")
            results['nginx'] = "NON INSTALLÉ"
    except Exception as e:
        print(f"   ❌ Erreur Nginx: {e}")
        results['nginx'] = f"ERREUR: {e}"
    
    print("\n📱 4. Frontend Flutter")
    print("-" * 50)
    
    try:
        flutter_version = subprocess.run(['flutter', '--version'], 
                                       capture_output=True, text=True, timeout=10)
        if flutter_version.returncode == 0:
            print("   ✅ Flutter: INSTALLÉ")
            print("   📋 Version détectée")
            
            if os.path.exists('frontend'):
                print("   ✅ Projet Flutter: PRÉSENT")
                results['frontend'] = "PRÉSENT"
            else:
                print("   ❌ Projet Flutter: MANQUANT")
                results['frontend'] = "MANQUANT"
        else:
            print("   ❌ Flutter: NON INSTALLÉ")
            results['frontend'] = "NON INSTALLÉ"
    except Exception as e:
        print(f"   ❌ Erreur Flutter: {e}")
        results['frontend'] = f"ERREUR: {e}"
    
    print("\n🏆 5. Test Final Application Complète")
    print("-" * 50)
    
    try:
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
