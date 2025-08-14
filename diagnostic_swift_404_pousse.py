#!/usr/bin/env python3
"""
Diagnostic Poussé - Erreur 404 SWIFT
Analyse approfondie pour identifier la cause exacte de l'erreur 404
"""

import requests
import socket
import ssl
import json
import time
import subprocess
import os
from datetime import datetime
from urllib.parse import urlparse

def diagnostic_swift_404_pousse():
    print("🔍 DIAGNOSTIC POUSSÉ - ERREUR 404 SWIFT")
    print("="*80)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("="*80)
    
    results = {}
    
    # Test 1: Diagnostic Backend Local
    print("\n🔧 Test 1: Diagnostic Backend Local")
    print("-" * 50)
    
    try:
        # Vérification processus
        process_check = subprocess.run(
            ["ps", "aux", "|", "grep", "uvicorn"],
            shell=True, capture_output=True, text=True
        )
        print(f"   📊 Processus uvicorn: {len(process_check.stdout.splitlines())} trouvé(s)")
        
        # Vérification port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print("   ✅ Port 8000: OUVERT")
            results['backend_port'] = True
        else:
            print("   ❌ Port 8000: FERMÉ")
            results['backend_port'] = False
            return results
            
        # Test endpoints locaux
        endpoints = ['/', '/health', '/api/health', '/api/swift/status']
        for endpoint in endpoints:
            try:
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
                print(f"   ✅ {endpoint}: {response.status_code}")
                results[f'endpoint_{endpoint.replace("/", "_")}'] = response.status_code
            except Exception as e:
                print(f"   ❌ {endpoint}: Erreur - {e}")
                results[f'endpoint_{endpoint.replace("/", "_")}'] = f"Error: {e}"
                
    except Exception as e:
        print(f"   ❌ Erreur diagnostic backend: {e}")
        results['backend_error'] = str(e)
    
    # Test 2: Diagnostic Réseau SWIFT
    print("\n🌐 Test 2: Diagnostic Réseau SWIFT")
    print("-" * 50)
    
    swift_hosts = [
        "swift.com",
        "api.swift.com", 
        "swiftnet.swift.com",
        "www.swift.com"
    ]
    
    for host in swift_hosts:
        try:
            print(f"\n   🔍 Test {host}:")
            
            # Test DNS
            try:
                ip = socket.gethostbyname(host)
                print(f"      ✅ DNS: {ip}")
                results[f'dns_{host}'] = ip
            except Exception as e:
                print(f"      ❌ DNS: {e}")
                results[f'dns_{host}'] = f"Error: {e}"
                continue
            
            # Test Port 443
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                result = sock.connect_ex((host, 443))
                sock.close()
                
                if result == 0:
                    print(f"      ✅ Port 443: OUVERT")
                    results[f'port_443_{host}'] = True
                else:
                    print(f"      ❌ Port 443: FERMÉ")
                    results[f'port_443_{host}'] = False
                    continue
            except Exception as e:
                print(f"      ❌ Port 443: {e}")
                results[f'port_443_{host}'] = f"Error: {e}"
                continue
            
            # Test SSL/TLS
            try:
                context = ssl.create_default_context()
                with socket.create_connection((host, 443), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=host) as ssock:
                        cert = ssock.getpeercert()
                        if cert:
                            print(f"      ✅ SSL: Certificat valide")
                            print(f"         📋 Sujet: {cert.get('subject', 'N/A')}")
                            print(f"         📅 Expire: {cert.get('notAfter', 'N/A')}")
                            results[f'ssl_{host}'] = {
                                'valid': True,
                                'subject': cert.get('subject', 'N/A'),
                                'expires': cert.get('notAfter', 'N/A')
                            }
                        else:
                            print(f"      ❌ SSL: Pas de certificat")
                            results[f'ssl_{host}'] = {'valid': False}
            except Exception as e:
                print(f"      ❌ SSL: {e}")
                results[f'ssl_{host}'] = f"Error: {e}"
                
        except Exception as e:
            print(f"   ❌ Erreur test {host}: {e}")
            results[f'error_{host}'] = str(e)
    
    # Test 3: Diagnostic API SWIFT Spécifique
    print("\n🏦 Test 3: Diagnostic API SWIFT Spécifique")
    print("-" * 50)
    
    swift_api_urls = [
        "https://api.swift.com",
        "https://api.swift.com/",
        "https://api.swift.com/messages",
        "https://api.swift.com/health",
        "https://api.swift.com/status"
    ]
    
    for url in swift_api_urls:
        try:
            print(f"\n   🔍 Test {url}:")
            
            # Test GET
            try:
                response = requests.get(url, timeout=10, verify=True)
                print(f"      📊 GET Status: {response.status_code}")
                print(f"      📋 Headers: {dict(response.headers)}")
                results[f'get_{url.replace("https://", "").replace("/", "_")}'] = {
                    'status': response.status_code,
                    'headers': dict(response.headers)
                }
            except requests.exceptions.ConnectionError:
                print(f"      ❌ GET: Connexion refusée")
                results[f'get_{url.replace("https://", "").replace("/", "_")}'] = "Connection refused"
            except requests.exceptions.Timeout:
                print(f"      ❌ GET: Timeout")
                results[f'get_{url.replace("https://", "").replace("/", "_")}'] = "Timeout"
            except Exception as e:
                print(f"      ❌ GET: {e}")
                results[f'get_{url.replace("https://", "").replace("/", "_")}'] = f"Error: {e}"
                
        except Exception as e:
            print(f"   ❌ Erreur test {url}: {e}")
            results[f'error_{url.replace("https://", "").replace("/", "_")}'] = str(e)
    
    # Test 4: Diagnostic Certificats SWIFT
    print("\n🔐 Test 4: Diagnostic Certificats SWIFT")
    print("-" * 50)
    
    cert_paths = [
        "/workspace/banking-transfer-platform/certificates/swift_client.crt",
        "/workspace/banking-transfer-platform/certificates/swift_client.key",
        "/workspace/banking-transfer-platform/certificates/swiftnet_root_2019.cer"
    ]
    
    for cert_path in cert_paths:
        try:
            if os.path.exists(cert_path):
                size = os.path.getsize(cert_path)
                print(f"   ✅ {cert_path}: {size} bytes")
                results[f'cert_{os.path.basename(cert_path)}'] = {
                    'exists': True,
                    'size': size
                }
            else:
                print(f"   ❌ {cert_path}: N'EXISTE PAS")
                results[f'cert_{os.path.basename(cert_path)}'] = {
                    'exists': False,
                    'size': 0
                }
        except Exception as e:
            print(f"   ❌ Erreur {cert_path}: {e}")
            results[f'cert_{os.path.basename(cert_path)}'] = f"Error: {e}"
    
    # Test 5: Test Transfert avec Debug
    print("\n💸 Test 5: Test Transfert avec Debug")
    print("-" * 50)
    
    transfer_data = {
        "amount": 777.0,
        "currency": "USD",
        "sender_iban": "00010100000000000000139",
        "sender_name": "Compte BCC RDC",
        "recipient_bic": "LHVBEE22",
        "recipient_iban": "EE047700771001660150",
        "recipient_name": "Monese Ltd",
        "purpose": "Test diagnostic 404",
        "reference": "DIAG404"
    }
    
    try:
        print("   🔍 Envoi requête avec debug...")
        start_time = datetime.now()
        
        response = requests.post(
            "http://localhost:8000/api/transfers",
            json=transfer_data,
            timeout=30
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"   ⏱️ Durée: {duration:.2f} secondes")
        print(f"   📊 Status Code: {response.status_code}")
        print(f"   📋 Headers Response: {dict(response.headers)}")
        
        try:
            data = response.json()
            print(f"   📋 Response JSON: {json.dumps(data, indent=2)}")
            results['transfer_response'] = data
        except:
            print(f"   📋 Response Text: {response.text}")
            results['transfer_response'] = response.text
            
        results['transfer_status'] = response.status_code
        results['transfer_duration'] = duration
        
    except Exception as e:
        print(f"   ❌ Erreur transfert: {e}")
        results['transfer_error'] = str(e)
    
    # Test 6: Analyse Code Backend
    print("\n🔍 Test 6: Analyse Code Backend")
    print("-" * 50)
    
    try:
        # Vérifier le code de la fonction send_swift_message
        backend_file = "/workspace/banking-transfer-platform/backend/app/main_reel.py"
        
        if os.path.exists(backend_file):
            with open(backend_file, 'r') as f:
                content = f.read()
                
            # Chercher la fonction send_swift_message
            if 'def send_swift_message' in content:
                print("   ✅ Fonction send_swift_message: TROUVÉE")
                
                # Extraire l'URL SWIFT utilisée
                import re
                url_match = re.search(r'f"{SWIFT_CONFIG\[\'api_swift_url\'\]}/messages"', content)
                if url_match:
                    print("   ✅ URL SWIFT: https://api.swift.com/messages")
                    results['swift_url_used'] = "https://api.swift.com/messages"
                else:
                    print("   ❌ URL SWIFT: NON TROUVÉE")
                    results['swift_url_used'] = "Not found"
                    
                # Vérifier les headers
                if 'X-SWIFT-Signature' in content:
                    print("   ✅ Headers SWIFT: PRÉSENTS")
                    results['swift_headers'] = True
                else:
                    print("   ❌ Headers SWIFT: MANQUANTS")
                    results['swift_headers'] = False
                    
            else:
                print("   ❌ Fonction send_swift_message: NON TROUVÉE")
                results['swift_function'] = False
        else:
            print(f"   ❌ Fichier backend: {backend_file} N'EXISTE PAS")
            results['backend_file'] = False
            
    except Exception as e:
        print(f"   ❌ Erreur analyse code: {e}")
        results['code_analysis_error'] = str(e)
    
    # Test 7: Test HTTP Direct vers SWIFT
    print("\n🌐 Test 7: Test HTTP Direct vers SWIFT")
    print("-" * 50)
    
    try:
        # Test direct vers l'endpoint SWIFT
        swift_url = "https://api.swift.com/messages"
        
        print(f"   🔍 Test direct vers: {swift_url}")
        
        # Test GET
        try:
            response = requests.get(swift_url, timeout=10, verify=True)
            print(f"      📊 GET Status: {response.status_code}")
            print(f"      📋 Response: {response.text[:200]}...")
            results['direct_swift_get'] = {
                'status': response.status_code,
                'response': response.text[:200]
            }
        except Exception as e:
            print(f"      ❌ GET: {e}")
            results['direct_swift_get'] = f"Error: {e}"
        
        # Test POST avec données minimales
        try:
            test_data = {
                "test": "message",
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(swift_url, json=test_data, timeout=10, verify=True)
            print(f"      📊 POST Status: {response.status_code}")
            print(f"      📋 Response: {response.text[:200]}...")
            results['direct_swift_post'] = {
                'status': response.status_code,
                'response': response.text[:200]
            }
        except Exception as e:
            print(f"      ❌ POST: {e}")
            results['direct_swift_post'] = f"Error: {e}"
            
    except Exception as e:
        print(f"   ❌ Erreur test direct: {e}")
        results['direct_swift_error'] = str(e)
    
    return results

def analyser_causes_404(results):
    print("\n" + "="*80)
    print("🔍 ANALYSE DES CAUSES DE L'ERREUR 404")
    print("="*80)
    
    causes = []
    
    # Analyse 1: Endpoint SWIFT inexistant
    if 'direct_swift_post' in results:
        if isinstance(results['direct_swift_post'], dict) and results['direct_swift_post'].get('status') == 404:
            causes.append("❌ CAUSE 1: Endpoint /messages n'existe pas sur api.swift.com")
        elif isinstance(results['direct_swift_post'], dict) and results['direct_swift_post'].get('status') == 401:
            causes.append("❌ CAUSE 2: Authentification SWIFT requise")
        elif isinstance(results['direct_swift_post'], dict) and results['direct_swift_post'].get('status') == 403:
            causes.append("❌ CAUSE 3: Accès interdit - Credentials SWIFT invalides")
    
    # Analyse 2: URL SWIFT incorrecte
    if 'swift_url_used' in results:
        if results['swift_url_used'] != "https://api.swift.com/messages":
            causes.append("❌ CAUSE 4: URL SWIFT incorrecte dans le code")
    
    # Analyse 3: Headers SWIFT manquants
    if 'swift_headers' in results and not results['swift_headers']:
        causes.append("❌ CAUSE 5: Headers d'authentification SWIFT manquants")
    
    # Analyse 4: Certificats SWIFT manquants
    cert_errors = []
    for key, value in results.items():
        if key.startswith('cert_') and isinstance(value, dict) and not value.get('exists'):
            cert_errors.append(key.replace('cert_', ''))
    
    if cert_errors:
        causes.append(f"❌ CAUSE 6: Certificats SWIFT manquants: {', '.join(cert_errors)}")
    
    # Analyse 5: Connectivité réseau
    if 'dns_api.swift.com' in results and isinstance(results['dns_api.swift.com'], str) and 'Error' in results['dns_api.swift.com']:
        causes.append("❌ CAUSE 7: Résolution DNS échouée pour api.swift.com")
    
    if 'port_443_api.swift.com' in results and not results['port_443_api.swift.com']:
        causes.append("❌ CAUSE 8: Port 443 fermé sur api.swift.com")
    
    # Analyse 6: SSL/TLS
    if 'ssl_api.swift.com' in results and isinstance(results['ssl_api.swift.com'], str) and 'Error' in results['ssl_api.swift.com']:
        causes.append("❌ CAUSE 9: Erreur SSL/TLS avec api.swift.com")
    
    # Si aucune cause spécifique trouvée
    if not causes:
        causes.append("❓ CAUSE INCONNUE: Erreur 404 SWIFT - Analyse approfondie requise")
    
    return causes

if __name__ == "__main__":
    try:
        print("🚀 Démarrage du diagnostic poussé...")
        results = diagnostic_swift_404_pousse()
        
        causes = analyser_causes_404(results)
        
        print("\n" + "="*80)
        print("🏆 RÉSULTATS DU DIAGNOSTIC POUSSÉ")
        print("="*80)
        
        print("\n📋 CAUSES IDENTIFIÉES:")
        for i, cause in enumerate(causes, 1):
            print(f"   {i}. {cause}")
        
        print("\n📊 RÉSUMÉ TECHNIQUE:")
        print(f"   🔧 Backend: {'✅ OPÉRATIONNEL' if results.get('backend_port') else '❌ PROBLÈME'}")
        print(f"   🌐 SWIFT DNS: {'✅ RÉSOLU' if 'dns_api.swift.com' in results and not isinstance(results['dns_api.swift.com'], str) else '❌ PROBLÈME'}")
        print(f"   🔐 Certificats: {'✅ PRÉSENTS' if not any(k.startswith('cert_') and isinstance(v, dict) and not v.get('exists') for k, v in results.items()) else '❌ MANQUANTS'}")
        print(f"   🏦 API SWIFT: {'✅ ACCESSIBLE' if 'direct_swift_get' in results and isinstance(results['direct_swift_get'], dict) else '❌ INACCESSIBLE'}")
        
        print("\n🎯 RECOMMANDATIONS:")
        if "Endpoint /messages n'existe pas" in str(causes):
            print("   🔧 Vérifier la documentation SWIFT pour l'endpoint correct")
        if "Authentification SWIFT requise" in str(causes):
            print("   🔐 Obtenir les vraies credentials SWIFT de production")
        if "Certificats SWIFT manquants" in str(causes):
            print("   📜 Installer les certificats SWIFT requis")
        
        print("\n💾 Résultats complets sauvegardés dans 'diagnostic_swift_404_results.json'")
        
        # Sauvegarder les résultats
        with open('diagnostic_swift_404_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
            
    except Exception as e:
        print(f"\n❌ ERREUR GÉNÉRALE: {e}")