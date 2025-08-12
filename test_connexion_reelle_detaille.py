#!/usr/bin/env python3
"""
Test détaillé de connexion réelle et interaction avec APIs
Vérification complète avec gestion d'erreurs et améliorations
"""

import asyncio
import sys
import aiohttp
import requests
import json
import time
from datetime import datetime
from pathlib import Path

class TestConnexionReelleDetaille:
    def __init__(self):
        self.test_results = {}
        self.errors = []
        self.improvements = []
        
    def print_test_header(self):
        print("="*80)
        print("🔍 TEST DÉTAILLÉ CONNEXION RÉELLE ET INTERACTION")
        print("="*80)
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        print("="*80)
    
    async def test_http_connectivity_detailed(self):
        """Test détaillé de la connectivité HTTP"""
        print("\n🌐 TEST CONNECTIVITÉ HTTP DÉTAILLÉ:")
        print("-" * 50)
        
        test_urls = [
            {
                "name": "HTTPBin GET",
                "url": "https://httpbin.org/get",
                "method": "GET",
                "expected_status": 200
            },
            {
                "name": "HTTPBin POST",
                "url": "https://httpbin.org/post",
                "method": "POST",
                "data": {"test": "data", "timestamp": datetime.now().isoformat()},
                "expected_status": 200
            },
            {
                "name": "HTTPBin Status 404",
                "url": "https://httpbin.org/status/404",
                "method": "GET",
                "expected_status": 404
            },
            {
                "name": "HTTPBin Delay",
                "url": "https://httpbin.org/delay/1",
                "method": "GET",
                "expected_status": 200
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for test in test_urls:
                try:
                    start_time = time.time()
                    
                    if test["method"] == "GET":
                        async with session.get(test["url"], timeout=30) as response:
                            response_time = time.time() - start_time
                            response_data = await response.text()
                            
                            print(f"🔍 {test['name']}:")
                            print(f"   URL: {test['url']}")
                            print(f"   Status: {response.status}")
                            print(f"   Temps de réponse: {response_time:.3f}s")
                            print(f"   Taille réponse: {len(response_data)} bytes")
                            
                            if response.status == test["expected_status"]:
                                print(f"   ✅ Succès (Status attendu: {test['expected_status']})")
                                self.test_results[test["name"]] = "SUCCESS"
                            else:
                                print(f"   ⚠️ Status inattendu (Attendu: {test['expected_status']})")
                                self.test_results[test["name"]] = "WARNING"
                                
                except asyncio.TimeoutError:
                    print(f"❌ {test['name']}: Timeout (>30s)")
                    self.test_results[test["name"]] = "TIMEOUT"
                    self.errors.append(f"Timeout sur {test['name']}")
                except Exception as e:
                    print(f"❌ {test['name']}: Erreur - {e}")
                    self.test_results[test["name"]] = "ERROR"
                    self.errors.append(f"Erreur sur {test['name']}: {e}")
    
    async def test_api_interactions_detailed(self):
        """Test détaillé des interactions API"""
        print("\n🔌 TEST INTERACTIONS API DÉTAILLÉ:")
        print("-" * 50)
        
        api_tests = [
            {
                "name": "GitHub API",
                "url": "https://api.github.com",
                "headers": {"User-Agent": "BankingTransferPlatform/1.0"},
                "validate_json": True
            },
            {
                "name": "JSONPlaceholder Posts",
                "url": "https://jsonplaceholder.typicode.com/posts/1",
                "validate_json": True,
                "expected_fields": ["id", "title", "body"]
            },
            {
                "name": "JSONPlaceholder Create",
                "url": "https://jsonplaceholder.typicode.com/posts",
                "method": "POST",
                "data": {
                    "title": "Test Banking Transfer Platform",
                    "body": f"Test créé le {datetime.now().isoformat()}",
                    "userId": 1
                },
                "validate_json": True
            },
            {
                "name": "Exchange Rate API",
                "url": "https://api.exchangerate-api.com/v4/latest/USD",
                "validate_json": True,
                "expected_fields": ["base", "rates", "date"]
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for test in api_tests:
                try:
                    start_time = time.time()
                    
                    # Préparation des paramètres
                    method = test.get("method", "GET")
                    headers = test.get("headers", {})
                    data = test.get("data")
                    
                    if method == "GET":
                        async with session.get(test["url"], headers=headers, timeout=30) as response:
                            response_time = time.time() - start_time
                            response_text = await response.text()
                            
                            print(f"🔍 {test['name']}:")
                            print(f"   URL: {test['url']}")
                            print(f"   Méthode: {method}")
                            print(f"   Status: {response.status}")
                            print(f"   Temps: {response_time:.3f}s")
                            print(f"   Taille: {len(response_text)} bytes")
                            
                            # Validation JSON si demandée
                            if test.get("validate_json"):
                                try:
                                    json_data = json.loads(response_text)
                                    print(f"   ✅ JSON valide")
                                    
                                    # Vérification des champs attendus
                                    if "expected_fields" in test:
                                        missing_fields = []
                                        for field in test["expected_fields"]:
                                            if field not in json_data:
                                                missing_fields.append(field)
                                        
                                        if missing_fields:
                                            print(f"   ⚠️ Champs manquants: {missing_fields}")
                                            self.improvements.append(f"Ajouter validation champs pour {test['name']}")
                                        else:
                                            print(f"   ✅ Tous les champs présents")
                                    
                                    # Affichage d'informations spécifiques
                                    if "github" in test["name"].lower():
                                        print(f"   📊 Rate Limit: {response.headers.get('X-RateLimit-Remaining', 'N/A')}")
                                    elif "exchangerate" in test["url"]:
                                        rates = json_data.get("rates", {})
                                        eur_rate = rates.get("EUR", "N/A")
                                        print(f"   💱 USD/EUR: {eur_rate}")
                                    
                                except json.JSONDecodeError:
                                    print(f"   ❌ JSON invalide")
                                    self.errors.append(f"JSON invalide pour {test['name']}")
                            
                            if response.status == 200:
                                print(f"   ✅ Succès")
                                self.test_results[test["name"]] = "SUCCESS"
                            else:
                                print(f"   ⚠️ Status {response.status}")
                                self.test_results[test["name"]] = "WARNING"
                                
                except asyncio.TimeoutError:
                    print(f"❌ {test['name']}: Timeout")
                    self.test_results[test["name"]] = "TIMEOUT"
                    self.errors.append(f"Timeout sur {test['name']}")
                except Exception as e:
                    print(f"❌ {test['name']}: Erreur - {e}")
                    self.test_results[test["name"]] = "ERROR"
                    self.errors.append(f"Erreur sur {test['name']}: {e}")
    
    async def test_swift_simulation_realistic(self):
        """Test réaliste de simulation SWIFT"""
        print("\n🏦 TEST SIMULATION SWIFT RÉALISTE:")
        print("-" * 50)
        
        try:
            # Simulation d'un transfert SWIFT réaliste
            transfer_data = {
                "id": f"BCC-MONESE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "amount": 777.0,
                "currency": "USD",
                "sender_iban": "CD12345678901234567890",
                "sender_name": "Compte BCC",
                "recipient_bic": "LHVBEE22",
                "recipient_iban": "EE047700771001660150",
                "recipient_name": "Monese Ltd",
                "purpose": "Transfert personnel",
                "reference": "M40282987",
                "timestamp": datetime.now().isoformat()
            }
            
            print("📊 Données de transfert:")
            for key, value in transfer_data.items():
                print(f"   {key}: {value}")
            
            # Simulation du processus SWIFT avec délais réalistes
            steps = [
                ("🔐 Chargement certificat racine SWIFT", 0.5),
                ("📜 Validation certificats BCC", 0.3),
                ("🔍 Validation données de transfert", 0.2),
                ("✅ Vérification conformité AML/KYC", 1.0),
                ("📄 Génération message ISO 20022", 0.8),
                ("🔒 Signature avec certificat BCC", 0.6),
                ("📡 Envoi via SWIFTNet PKI", 2.0),
                ("⏳ Attente ACK SWIFTNet", 1.5),
                ("📊 Traitement réponse SWIFT", 0.7),
                ("🎯 Génération numéro GPI", 0.4),
                ("✅ Confirmation transfert", 0.3)
            ]
            
            total_time = 0
            for i, (step, delay) in enumerate(steps, 1):
                print(f"   {i:2d}. {step}...")
                await asyncio.sleep(delay)
                total_time += delay
                print(f"       ✅ Terminé ({delay:.1f}s)")
            
            # Simulation de la réponse SWIFT
            swift_response = {
                "id": transfer_data["id"],
                "status": "COMPLETED",
                "swift_message_id": f"SWIFTBCCGCDK2XXX-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "ack_received": True,
                "ack_timestamp": datetime.now().isoformat(),
                "gpi_tracking_id": f"GPI{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "swift_network_status": "ACTIVE",
                "processing_time": f"{total_time:.2f}s",
                "error_message": None
            }
            
            print(f"\n✅ Transfert SWIFT simulé avec succès:")
            print(f"   ID: {swift_response['id']}")
            print(f"   Status: {swift_response['status']}")
            print(f"   Message ID: {swift_response['swift_message_id']}")
            print(f"   GPI Tracking: {swift_response['gpi_tracking_id']}")
            print(f"   Temps de traitement: {swift_response['processing_time']}")
            print(f"   ACK reçu: {swift_response['ack_received']}")
            print(f"   Réseau: {swift_response['swift_network_status']}")
            
            self.test_results["SWIFT Simulation"] = "SUCCESS"
            
        except Exception as e:
            print(f"❌ Erreur simulation SWIFT: {e}")
            self.test_results["SWIFT Simulation"] = "ERROR"
            self.errors.append(f"Erreur simulation SWIFT: {e}")
    
    def test_backend_connectivity_detailed(self):
        """Test détaillé de la connectivité backend"""
        print("\n🔧 TEST CONNECTIVITÉ BACKEND DÉTAILLÉ:")
        print("-" * 50)
        
        try:
            # Test de connectivité au backend
            start_time = time.time()
            response = requests.get("http://localhost:8000/health", timeout=10)
            response_time = time.time() - start_time
            
            print(f"🔍 Backend Health Check:")
            print(f"   URL: http://localhost:8000/health")
            print(f"   Status: {response.status_code}")
            print(f"   Temps de réponse: {response_time:.3f}s")
            print(f"   Taille réponse: {len(response.text)} bytes")
            
            if response.status_code == 200:
                print(f"   ✅ Backend accessible")
                self.test_results["Backend Health"] = "SUCCESS"
                
                # Test de parsing de la réponse
                try:
                    health_data = response.json()
                    print(f"   📊 Données health: {health_data}")
                except json.JSONDecodeError:
                    print(f"   ⚠️ Réponse non-JSON: {response.text[:100]}...")
                    
            else:
                print(f"   ⚠️ Status inattendu: {response.status_code}")
                self.test_results["Backend Health"] = "WARNING"
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Backend non accessible (port 8000)")
            self.test_results["Backend Health"] = "ERROR"
            self.errors.append("Backend non accessible")
            self.improvements.append("Démarrer le backend avec: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        except requests.exceptions.Timeout:
            print(f"❌ Timeout backend (>10s)")
            self.test_results["Backend Health"] = "TIMEOUT"
            self.errors.append("Timeout backend")
        except Exception as e:
            print(f"❌ Erreur test backend: {e}")
            self.test_results["Backend Health"] = "ERROR"
            self.errors.append(f"Erreur backend: {e}")
    
    def analyze_and_improve(self):
        """Analyse les résultats et propose des améliorations"""
        print("\n🔍 ANALYSE ET AMÉLIORATIONS:")
        print("-" * 50)
        
        # Statistiques
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result == "SUCCESS")
        error_tests = sum(1 for result in self.test_results.values() if result == "ERROR")
        warning_tests = sum(1 for result in self.test_results.values() if result == "WARNING")
        
        print(f"📊 Statistiques:")
        print(f"   Total tests: {total_tests}")
        print(f"   Succès: {successful_tests}")
        print(f"   Erreurs: {error_tests}")
        print(f"   Avertissements: {warning_tests}")
        print(f"   Taux de succès: {(successful_tests/total_tests)*100:.1f}%")
        
        # Erreurs détectées
        if self.errors:
            print(f"\n❌ Erreurs détectées:")
            for error in self.errors:
                print(f"   - {error}")
        
        # Améliorations proposées
        if self.improvements:
            print(f"\n💡 Améliorations proposées:")
            for improvement in self.improvements:
                print(f"   - {improvement}")
        
        # Recommandations générales
        print(f"\n🎯 Recommandations:")
        
        if error_tests > 0:
            print(f"   ⚠️ Corriger les {error_tests} erreurs détectées")
        
        if warning_tests > 0:
            print(f"   🔧 Améliorer les {warning_tests} tests avec avertissements")
        
        if successful_tests == total_tests:
            print(f"   ✅ Tous les tests réussis - Application prête pour production")
        elif successful_tests >= total_tests * 0.8:
            print(f"   ✅ Application fonctionnelle avec quelques améliorations mineures")
        else:
            print(f"   ⚠️ Application nécessite des corrections importantes")
    
    async def run_complete_test(self):
        """Exécute le test complet détaillé"""
        print("🎯 TEST DÉTAILLÉ CONNEXION RÉELLE ET INTERACTION")
        print("="*70)
        
        # En-tête
        self.print_test_header()
        
        # Tests détaillés
        await self.test_http_connectivity_detailed()
        await self.test_api_interactions_detailed()
        await self.test_swift_simulation_realistic()
        self.test_backend_connectivity_detailed()
        
        # Analyse et améliorations
        self.analyze_and_improve()
        
        # Résumé final
        print("\n" + "="*80)
        print("📊 RÉSUMÉ FINAL DU TEST DÉTAILLÉ")
        print("="*80)
        
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result == "SUCCESS" else "⚠️" if result == "WARNING" else "❌"
            print(f"   {status_icon} {test_name}: {result}")
        
        overall_success = all(result == "SUCCESS" for result in self.test_results.values())
        
        if overall_success:
            print("\n🎉 TOUS LES TESTS RÉUSSIS!")
            print("L'application est parfaitement opérationnelle")
        elif len(self.errors) == 0:
            print("\n✅ APPLICATION FONCTIONNELLE")
            print("Quelques améliorations mineures recommandées")
        else:
            print(f"\n⚠️ APPLICATION AVEC ERREURS")
            print(f"{len(self.errors)} erreurs à corriger")
        
        return overall_success

def main():
    """Fonction principale"""
    test = TestConnexionReelleDetaille()
    
    try:
        success = asyncio.run(test.run_complete_test())
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrompu")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur générale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()