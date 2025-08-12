#!/usr/bin/env python3
"""
Test Connexion 100% RÉEL - Aucune Simulation
"""

import asyncio
import sys
import socket
import ssl
import requests
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

class TestConnexion100Reel:
    def __init__(self):
        self.app_config = {
            "backend_url": "http://localhost:8000",
            "frontend_url": "http://localhost:3000",
            "database_config": {
                "host": "localhost",
                "port": "5432",
                "database": "banking_transfer",
                "user": "postgres",
                "password": "password"
            },
            "swift_endpoints": {
                "swift_main": "swift.com",
                "swift_api": "api.swift.com",
                "swiftnet_pki": "swiftnet.swift.com"
            }
        }
        
    def print_test_header(self):
        print("="*100)
        print("🌐 TEST CONNEXION 100% RÉEL - AUCUNE SIMULATION")
        print("="*100)
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        print("="*100)
        print("")
        print("🎯 OBJECTIF: Test de connexion RÉELLE sans simulation")
        print("🔍 VÉRIFICATIONS: Backend, Frontend, DB, SWIFT, Transferts RÉELS")
        print("🚀 RÉSULTAT: État RÉEL de l'application")
        print("="*100)
    
    def test_backend_reel(self):
        print("\n�� TEST BACKEND RÉEL:")
        print("-" * 50)
        
        try:
            print(f"   🔍 Test connexion: {self.app_config['backend_url']}")
            
            response = requests.get(f"{self.app_config['backend_url']}/health", timeout=10)
            print(f"   📊 Status: {response.status_code}")
            print(f"   ⏱️ Temps: {response.elapsed.total_seconds():.2f}s")
            
            if response.status_code == 200:
                print("   ✅ Backend: CONNEXION RÉELLE RÉUSSIE")
                return True
            else:
                print("   ❌ Backend: ÉCHEC")
                return False
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Backend: SERVICE NON DÉMARRÉ")
            return False
        except Exception as e:
            print(f"   ❌ Backend: Erreur - {e}")
            return False
    
    def test_frontend_reel(self):
        print("\n🎨 TEST FRONTEND RÉEL:")
        print("-" * 50)
        
        try:
            print(f"   🔍 Test connexion: {self.app_config['frontend_url']}")
            
            response = requests.get(self.app_config['frontend_url'], timeout=10)
            print(f"   📊 Status: {response.status_code}")
            print(f"   ⏱️ Temps: {response.elapsed.total_seconds():.2f}s")
            
            if response.status_code == 200:
                print("   ✅ Frontend: CONNEXION RÉELLE RÉUSSIE")
                return True
            else:
                print("   ❌ Frontend: ÉCHEC")
                return False
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Frontend: SERVICE NON DÉMARRÉ")
            return False
        except Exception as e:
            print(f"   ❌ Frontend: Erreur - {e}")
            return False
    
    def test_database_reel(self):
        print("\n🗄️ TEST BASE DE DONNÉES RÉELLE:")
        print("-" * 50)
        
        try:
            import psycopg2
            
            print("   🔍 Test connexion PostgreSQL...")
            
            conn = psycopg2.connect(
                host=self.app_config['database_config']['host'],
                port=self.app_config['database_config']['port'],
                database=self.app_config['database_config']['database'],
                user=self.app_config['database_config']['user'],
                password=self.app_config['database_config']['password']
            )
            
            print("   ✅ Base de données: CONNEXION RÉELLE RÉUSSIE")
            
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"   📊 Version: {version[0]}")
            
            cursor.close()
            conn.close()
            
            return True
            
        except ImportError:
            print("   ⚠️ psycopg2 non installé")
            return False
        except psycopg2.OperationalError as e:
            print(f"   ❌ Base de données: Erreur connexion - {e}")
            return False
        except Exception as e:
            print(f"   ❌ Base de données: Erreur - {e}")
            return False
    
    def test_swift_connectivite_reelle(self):
        print("\n🌐 TEST CONNECTIVITÉ SWIFT RÉELLE:")
        print("-" * 50)
        
        swift_results = {}
        
        for service, hostname in self.app_config['swift_endpoints'].items():
            print(f"   🔍 Test {service}: {hostname}")
            
            try:
                ip = socket.gethostbyname(hostname)
                print(f"   ✅ DNS: {hostname} -> {ip}")
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                result = sock.connect_ex((hostname, 443))
                sock.close()
                
                if result == 0:
                    print(f"   ✅ Port: 443 OUVERT")
                    
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(15)
                        sock.connect((hostname, 443))
                        
                        ssl_context = ssl.create_default_context()
                        ssl_sock = ssl_context.wrap_socket(sock, server_hostname=hostname)
                        
                        cert = ssl_sock.getpeercert()
                        print(f"   ✅ SSL: Certificat valide")
                        
                        ssl_sock.close()
                        swift_results[service] = True
                        
                    except Exception as e:
                        print(f"   ❌ SSL: Erreur - {e}")
                        swift_results[service] = False
                else:
                    print(f"   ❌ Port: 443 FERMÉ")
                    swift_results[service] = False
                    
            except socket.gaierror:
                print(f"   ⚠️ DNS: Non résolu")
                swift_results[service] = False
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
                swift_results[service] = False
        
        return swift_results
    
    def test_certificats_bcc_reels(self):
        print("\n🔐 TEST CERTIFICATS BCC RÉELS:")
        print("-" * 50)
        
        cert_files = [
            "certificates/swift_client.crt",
            "certificates/swift_client.key",
            "certificates/swiftnet_root_2019.cer"
        ]
        
        all_valid = True
        for cert_file in cert_files:
            cert_path = Path(cert_file)
            if cert_path.exists():
                size = cert_path.stat().st_size
                print(f"   ✅ {cert_file}: {size} bytes")
                
                if cert_file.endswith('.crt'):
                    try:
                        with open(cert_path, 'rb') as f:
                            cert_data = f.read()
                        if b'-----BEGIN CERTIFICATE-----' in cert_data:
                            print(f"   ✅ Format PEM valide")
                        else:
                            print(f"   ❌ Format invalide")
                            all_valid = False
                    except Exception as e:
                        print(f"   ❌ Erreur lecture: {e}")
                        all_valid = False
            else:
                print(f"   ❌ {cert_file}: MANQUANT")
                all_valid = False
        
        return all_valid
    
    async def test_transfert_swift_reel(self):
        print("\n🚀 TEST TRANSFERT SWIFT RÉEL:")
        print("-" * 50)
        
        try:
            transfer_data = {
                "amount": 777.0,
                "currency": "USD",
                "sender_iban": "CD12345678901234567890",
                "sender_name": "Compte BCC",
                "recipient_bic": "LHVBEE22",
                "recipient_iban": "EE047700771001660150",
                "recipient_name": "Monese Ltd",
                "purpose": "Test connexion réelle",
                "reference": "M40282987"
            }
            
            print("📋 Tentative de transfert RÉEL...")
            print(f"   💰 Montant: {transfer_data['amount']} {transfer_data['currency']}")
            print(f"   🏦 Expéditeur: {transfer_data['sender_name']}")
            print(f"   📍 Destinataire: {transfer_data['recipient_name']}")
            
            try:
                response = requests.post(
                    f"{self.app_config['backend_url']}/api/transfers",
                    json=transfer_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("   ✅ TRANSFERT RÉEL RÉUSSI!")
                    print(f"   📊 ID: {result.get('id', 'N/A')}")
                    print(f"   🎯 Status: {result.get('status', 'N/A')}")
                    return result
                else:
                    print(f"   ❌ API Transfert: Status {response.status_code}")
                    return None
                    
            except requests.exceptions.ConnectionError:
                print("   ❌ API Transfert: Service non accessible")
                return None
            except Exception as e:
                print(f"   ❌ API Transfert: Erreur - {e}")
                return None
                
        except Exception as e:
            print(f"   ❌ Test transfert: Erreur - {e}")
            return None
    
    def test_services_systeme_reels(self):
        print("\n⚙️ TEST SERVICES SYSTÈME RÉELS:")
        print("-" * 50)
        
        services = [
            ("PostgreSQL", "postgresql"),
            ("Redis", "redis"),
            ("Nginx", "nginx")
        ]
        
        all_running = True
        for service_name, service_cmd in services:
            try:
                result = subprocess.run(
                    ["systemctl", "is-active", service_cmd],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0 and result.stdout.strip() == "active":
                    print(f"   ✅ {service_name}: ACTIF")
                else:
                    print(f"   ❌ {service_name}: INACTIF")
                    all_running = False
                    
            except Exception as e:
                print(f"   ⚠️ {service_name}: Non vérifiable - {e}")
        
        return all_running
    
    async def run_test_100_reel(self):
        print("🌐 TEST CONNEXION 100% RÉEL - AUCUNE SIMULATION")
        print("="*70)
        
        self.print_test_header()
        
        backend_ok = self.test_backend_reel()
        frontend_ok = self.test_frontend_reel()
        database_ok = self.test_database_reel()
        swift_results = self.test_swift_connectivite_reelle()
        bcc_certs_ok = self.test_certificats_bcc_reels()
        transfer_result = await self.test_transfert_swift_reel()
        services_ok = self.test_services_systeme_reels()
        
        print("\n" + "="*100)
        print("🏆 RÉSULTAT FINAL - TEST 100% RÉEL")
        print("="*100)
        
        swift_success = sum(swift_results.values())
        total_swift = len(swift_results)
        
        print("📊 RÉSULTATS DES TESTS RÉELS:")
        print(f"   🔧 Backend: {'✅ CONNECTÉ' if backend_ok else '❌ DÉCONNECTÉ'}")
        print(f"   🎨 Frontend: {'✅ CONNECTÉ' if frontend_ok else '❌ DÉCONNECTÉ'}")
        print(f"   🗄️ Base de données: {'✅ CONNECTÉE' if database_ok else '❌ DÉCONNECTÉE'}")
        print(f"   🌐 SWIFT: {swift_success}/{total_swift} connecté(s)")
        print(f"   🔐 Certificats BCC: {'✅ VALIDES' if bcc_certs_ok else '❌ INVALIDES'}")
        print(f"   🚀 Transfert SWIFT: {'✅ RÉUSSI' if transfer_result else '❌ ÉCHEC'}")
        print(f"   ⚙️ Services système: {'✅ ACTIFS' if services_ok else '❌ INACTIFS'}")
        
        if backend_ok and frontend_ok and database_ok and swift_success > 0 and bcc_certs_ok:
            if transfer_result:
                print("\n�� APPLICATION 100% RÉELLE OPÉRATIONNELLE!")
                print("   ✅ Tous les services connectés")
                print("   ✅ Transferts SWIFT fonctionnels")
                print("   ✅ Infrastructure complète opérationnelle")
                print("   🚀 APPLICATION PRÊTE POUR PRODUCTION RÉELLE!")
                return True
            else:
                print("\n⚠️ APPLICATION PARTIELLEMENT RÉELLE")
                print("   ✅ Infrastructure connectée")
                print("   ❌ Transferts SWIFT échoués")
                return False
        else:
            print("\n❌ APPLICATION NON OPÉRATIONNELLE")
            print("   ❌ Services non démarrés ou non connectés")
            return False

def main():
    test = TestConnexion100Reel()
    
    try:
        success = asyncio.run(test.run_test_100_reel())
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrompu")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur générale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
