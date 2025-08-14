#!/usr/bin/env python3
"""
Test Connexion Backend 100% RÉEL
"""

import requests
import socket
import time
import subprocess
import psutil
from datetime import datetime

def test_connexion_backend_100_reel():
    print("🔧 TEST CONNEXION BACKEND 100% RÉEL")
    print("="*60)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("="*60)
    
    print("\n🔍 Test 1: Processus Backend")
    print("-" * 40)
    
    backend_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'uvicorn' in proc.info['name'] or 'python' in proc.info['name']:
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if 'app.main:app' in cmdline or '8000' in cmdline:
                    backend_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if backend_processes:
        print("   ✅ Processus backend trouvé(s):")
        for proc in backend_processes:
            print(f"   �� PID: {proc['pid']}")
            print(f"   📄 Commande: {' '.join(proc['cmdline'])}")
    else:
        print("   ❌ Aucun processus backend trouvé")
        return False
    
    print("\n🔌 Test 2: Port 8000")
    print("-" * 40)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print("   ✅ Port 8000: OUVERT")
        else:
            print("   ❌ Port 8000: FERMÉ")
            return False
    except Exception as e:
        print(f"   ❌ Erreur test port: {e}")
        return False
    
    print("\n🌐 Test 3: HTTP Root Endpoint")
    print("-" * 40)
    
    try:
        start_time = time.time()
        response = requests.get("http://localhost:8000/", timeout=10)
        end_time = time.time()
        
        print(f"   📊 Status: {response.status_code}")
        print(f"   ⏱️ Temps: {(end_time - start_time)*1000:.2f}ms")
        
        if response.status_code == 200:
            print("   ✅ Root endpoint: OPÉRATIONNEL")
            try:
                data = response.json()
                print(f"   📋 Response: {data}")
            except:
                print(f"   📋 Response: {response.text[:200]}...")
        else:
            print(f"   ❌ Root endpoint: Status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Root endpoint: Connexion refusée")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ Root endpoint: Timeout")
        return False
    except Exception as e:
        print(f"   ❌ Root endpoint: Erreur - {e}")
        return False
    
    print("\n🏥 Test 4: HTTP Health Endpoint")
    print("-" * 40)
    
    try:
        start_time = time.time()
        response = requests.get("http://localhost:8000/health", timeout=10)
        end_time = time.time()
        
        print(f"   📊 Status: {response.status_code}")
        print(f"   ⏱️ Temps: {(end_time - start_time)*1000:.2f}ms")
        
        if response.status_code == 200:
            print("   ✅ Health endpoint: OPÉRATIONNEL")
            try:
                data = response.json()
                print(f"   📋 Response: {data}")
            except:
                print(f"   📋 Response: {response.text[:200]}...")
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
    
    print("\n�� Test 5: HTTP API Health Endpoint")
    print("-" * 40)
    
    try:
        start_time = time.time()
        response = requests.get("http://localhost:8000/api/health", timeout=10)
        end_time = time.time()
        
        print(f"   📊 Status: {response.status_code}")
        print(f"   ⏱️ Temps: {(end_time - start_time)*1000:.2f}ms")
        
        if response.status_code == 200:
            print("   ✅ API Health endpoint: OPÉRATIONNEL")
            try:
                data = response.json()
                print(f"   📋 Response: {data}")
            except:
                print(f"   📋 Response: {response.text[:200]}...")
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
    
    print("\n💸 Test 6: HTTP API Transfers Endpoint (GET)")
    print("-" * 40)
    
    try:
        start_time = time.time()
        response = requests.get("http://localhost:8000/api/transfers", timeout=10)
        end_time = time.time()
        
        print(f"   �� Status: {response.status_code}")
        print(f"   ⏱️ Temps: {(end_time - start_time)*1000:.2f}ms")
        
        if response.status_code == 200:
            print("   ✅ API Transfers GET: OPÉRATIONNEL")
            try:
                data = response.json()
                print(f"   📋 Response: {data}")
            except:
                print(f"   📋 Response: {response.text[:200]}...")
        else:
            print(f"   ❌ API Transfers GET: Status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ API Transfers GET: Connexion refusée")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ API Transfers GET: Timeout")
        return False
    except Exception as e:
        print(f"   ❌ API Transfers GET: Erreur - {e}")
        return False
    
    print("\n💸 Test 7: HTTP API Transfers Endpoint (POST)")
    print("-" * 40)
    
    transfer_data = {
        "amount": 777.0,
        "currency": "USD",
        "recipient_iban": "EE047700771001660150",
        "recipient_name": "Monese Ltd"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/api/transfers",
            json=transfer_data,
            timeout=10
        )
        end_time = time.time()
        
        print(f"   📊 Status: {response.status_code}")
        print(f"   ⏱️ Temps: {(end_time - start_time)*1000:.2f}ms")
        print(f"   📤 Data envoyée: {transfer_data}")
        
        if response.status_code == 200:
            print("   ✅ API Transfers POST: OPÉRATIONNEL")
            try:
                data = response.json()
                print(f"   📋 Response: {data}")
                print(f"   🆔 Transfert ID: {data.get('id', 'N/A')}")
                print(f"   🎯 Status: {data.get('status', 'N/A')}")
            except:
                print(f"   📋 Response: {response.text[:200]}...")
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
    
    print("\n⚡ Test 8: Performance Backend")
    print("-" * 40)
    
    times = []
    for i in range(5):
        try:
            start_time = time.time()
            response = requests.get("http://localhost:8000/health", timeout=5)
            end_time = time.time()
            
            if response.status_code == 200:
                times.append((end_time - start_time) * 1000)
                print(f"   📊 Test {i+1}: {times[-1]:.2f}ms")
            else:
                print(f"   ❌ Test {i+1}: Échec")
                
        except Exception as e:
            print(f"   ❌ Test {i+1}: Erreur - {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"   📈 Performance:")
        print(f"      Moyenne: {avg_time:.2f}ms")
        print(f"      Min: {min_time:.2f}ms")
        print(f"      Max: {max_time:.2f}ms")
        
        if avg_time < 100:
            print("   ✅ Performance: EXCELLENTE")
        elif avg_time < 500:
            print("   ✅ Performance: BONNE")
        else:
            print("   ⚠️ Performance: LENTE")
    
    print("\n" + "="*60)
    print("🏆 RÉSULTAT FINAL - CONNEXION BACKEND 100% RÉEL")
    print("="*60)
    
    print("✅ BACKEND 100% OPÉRATIONNEL!")
    print("   🔧 Processus: Démarré")
    print("   🔌 Port: Ouvert")
    print("   🌐 HTTP: Fonctionnel")
    print("   🚀 API: Opérationnelle")
    print("   💸 Transfers: Création réussie")
    print("   ⚡ Performance: Testée")
    
    print("\n🎯 CONNEXION BACKEND RÉELLE 100% RÉUSSIE!")
    print("   Aucune simulation - Tous les tests sont réels")
    
    return True

if __name__ == "__main__":
    try:
        success = test_connexion_backend_100_reel()
        if success:
            print("\n🎉 SUCCÈS: Backend 100% opérationnel!")
        else:
            print("\n❌ ÉCHEC: Problèmes détectés")
    except Exception as e:
        print(f"\n❌ ERREUR GÉNÉRALE: {e}")
