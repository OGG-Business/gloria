#!/usr/bin/env python3
"""
Diagnostic Backend Réel
Diagnostic du backend pour identifier les problèmes
"""

import subprocess
import socket
import time
from datetime import datetime

def diagnostic_backend_reel():
    print("🔍 DIAGNOSTIC BACKEND RÉEL")
    print("="*50)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("="*50)
    
    # Test 1: Vérifier les processus
    print("\n🔍 Test 1: Processus")
    print("-" * 30)
    
    try:
        result = subprocess.run(
            ["ps", "aux", "|", "grep", "uvicorn"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        print("   📊 Processus uvicorn:")
        print(result.stdout)
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 2: Vérifier le port avec netstat
    print("\n🔌 Test 2: Port avec netstat")
    print("-" * 30)
    
    try:
        result = subprocess.run(
            ["netstat", "-tlnp", "|", "grep", "8000"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        print("   📊 Port 8000:")
        print(result.stdout)
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 3: Test socket direct
    print("\n🔌 Test 3: Socket direct")
    print("-" * 30)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print("   ✅ Socket: Connexion réussie")
        else:
            print(f"   ❌ Socket: Erreur {result}")
    except Exception as e:
        print(f"   ❌ Socket: Erreur - {e}")
    
    # Test 4: Test avec telnet
    print("\n🔌 Test 4: Telnet")
    print("-" * 30)
    
    try:
        result = subprocess.run(
            ["timeout", "3", "telnet", "localhost", "8000"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print("   📊 Telnet résultat:")
        print(result.stdout)
        print("   📊 Telnet erreur:")
        print(result.stderr)
    except Exception as e:
        print(f"   ❌ Telnet: Erreur - {e}")
    
    # Test 5: Test avec wget
    print("\n🌐 Test 5: Wget")
    print("-" * 30)
    
    try:
        result = subprocess.run(
            ["timeout", "5", "wget", "-qO-", "http://localhost:8000/health"],
            capture_output=True,
            text=True,
            timeout=10
        )
        print("   📊 Wget résultat:")
        print(result.stdout)
        print("   📊 Wget erreur:")
        print(result.stderr)
    except Exception as e:
        print(f"   ❌ Wget: Erreur - {e}")
    
    # Test 6: Vérifier les logs du processus
    print("\n📄 Test 6: Logs du processus")
    print("-" * 30)
    
    try:
        result = subprocess.run(
            ["ps", "aux", "|", "grep", "uvicorn"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'uvicorn' in line and 'python' in line:
                    parts = line.split()
                    if len(parts) > 1:
                        pid = parts[1]
                        print(f"   📊 PID trouvé: {pid}")
                        
                        # Essayer de voir les logs du processus
                        try:
                            log_result = subprocess.run(
                                ["timeout", "2", "tail", "-f", "/proc/" + pid + "/fd/1"],
                                capture_output=True,
                                text=True,
                                timeout=3
                            )
                            print("   📄 Logs du processus:")
                            print(log_result.stdout)
                        except:
                            print("   ⚠️ Impossible de lire les logs")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n" + "="*50)
    print("🏆 DIAGNOSTIC TERMINÉ")
    print("="*50)
    print("📊 Vérifiez les résultats ci-dessus")
    print("🔧 Le backend semble avoir des problèmes de démarrage")

if __name__ == "__main__":
    diagnostic_backend_reel()