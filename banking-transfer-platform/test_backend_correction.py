#!/usr/bin/env python3
"""
Test Backend Correction
"""

import requests
import socket
import time
from datetime import datetime

def test_backend_correction():
    print("🔧 TEST BACKEND CORRECTION")
    print("="*50)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("="*50)
    
    print("\n🔌 Test 1: Port 8000")
    print("-" * 30)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print("   ✅ Port 8000: OUVERT")
        else:
            print("   ❌ Port 8000: FERMÉ")
            print("   🔧 Démarrons le backend...")
            
            import subprocess
            import os
            
            os.chdir('/workspace/banking-transfer-platform/backend')
            process = subprocess.Popen(
                ["python", "-m", "uvicorn", "app.main_simple:app", "--host", "0.0.0.0", "--port", "8000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            time.sleep(10)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('localhost', 8000))
            sock.close()
            
            if result == 0:
                print("   ✅ Port 8000: OUVERT (après démarrage)")
            else:
                print("   ❌ Port 8000: Toujours fermé")
                return False
    except Exception as e:
        print(f"   ❌ Erreur test port: {e}")
        return False
    
    print("\n🏥 Test 2: HTTP Health Endpoint")
    print("-" * 30)
    
    try:
        print("   🔍 Tentative de connexion...")
        response = requests.get("http://localhost:8000/health", timeout=10)
        
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Health endpoint: OPÉRATIONNEL")
            try:
                data = response.json()
                print(f"   📋 Response: {data}")
            except:
                print(f"   �� Response: {response.text[:100]}...")
        else:
            print(f"   ❌ Health endpoint: Status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Health endpoint: Connexion refusée")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ Health endpoint: Timeout")
        return False
    except Exception as e:
        print(f"   ❌ Health endpoint: Erreur - {e}")
        return False
    
    print("\n🚀 Test 3: HTTP API Health Endpoint")
    print("-" * 30)
    
    try:
        print("   🔍 Tentative de connexion...")
        response = requests.get("http://localhost:8000/api/health", timeout=10)
        
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ API Health endpoint: OPÉRATIONNEL")
            try:
                data = response.json()
                print(f"   📋 Response: {data}")
            except:
                print(f"   📋 Response: {response.text[:100]}...")
        else:
            print(f"   ❌ API Health endpoint: Status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ API Health endpoint: Connexion refusée")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ API Health endpoint: Timeout")
        return False
    except Exception as e:
        print(f"   ❌ API Health endpoint: Erreur - {e}")
        return False
    
    print("\n💸 Test 4: HTTP API Transfers Endpoint (POST)")
    print("-" * 30)
    
    transfer_data = {
        "amount": 777.0,
        "currency": "USD",
        "recipient_iban": "EE047700771001660150",
        "recipient_name": "Monese Ltd"
    }
    
    try:
        print("   🔍 Tentative de création de transfert...")
        response = requests.post(
            "http://localhost:8000/api/transfers",
            json=transfer_data,
            timeout=10
        )
        
        print(f"   📊 Status: {response.status_code}")
        print(f"   📤 Data envoyée: {transfer_data}")
        
        if response.status_code == 200:
            print("   ✅ API Transfers POST: OPÉRATIONNEL")
            try:
                data = response.json()
                print(f"   📋 Response: {data}")
                print(f"   🆔 Transfert ID: {data.get('id', 'N/A')}")
                print(f"   🎯 Status: {data.get('status', 'N/A')}")
            except:
                print(f"   📋 Response: {response.text[:100]}...")
        else:
            print(f"   ❌ API Transfers POST: Status {response.status_code}")
            print(f"   📋 Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ API Transfers POST: Connexion refusée")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ API Transfers POST: Timeout")
        return False
    except Exception as e:
        print(f"   ❌ API Transfers POST: Erreur - {e}")
        return False
    
    print("\n" + "="*50)
    print("🏆 RÉSULTAT FINAL - BACKEND CORRECTION")
    print("="*50)
    
    print("✅ BACKEND 100% OPÉRATIONNEL!")
    print("   🔌 Port: Ouvert")
    print("   🏥 Health: Fonctionnel")
    print("   🚀 API Health: Fonctionnel")
    print("   💸 Transfers: Création réussie")
    
    print("\n🎯 CORRECTION BACKEND RÉUSSIE!")
    print("   API FastAPI maintenant fonctionnelle")
    
    return True

if __name__ == "__main__":
    try:
        success = test_backend_correction()
        if success:
            print("\n🎉 SUCCÈS: Backend corrigé et opérationnel!")
        else:
            print("\n❌ ÉCHEC: Problèmes persistants")
    except Exception as e:
        print(f"\n❌ ERREUR GÉNÉRALE: {e}")
