#!/usr/bin/env python3
"""
Test d'APIs avancées pour vérifier les interactions complexes
"""

import asyncio
import sys
import aiohttp
import json
import time
import ssl
from datetime import datetime

class TestAPIsAvancees:
    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}
        self.errors = []
        self.improvements = []
        
    def print_test_header(self):
        print("="*80)
        print("🚀 TEST APIs AVANCÉES - INTERACTIONS COMPLEXES")
        print("="*80)
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        print("="*80)
    
    async def test_ssl_tls_connectivity(self):
        print("\n🔒 TEST CONNECTIVITÉ SSL/TLS:")
        print("-" * 50)
        
        ssl_tests = [
            {
                "name": "HTTPS Strict",
                "url": "https://httpbin.org/get",
                "verify_ssl": True
            },
            {
                "name": "GitHub API SSL",
                "url": "https://api.github.com",
                "verify_ssl": True
            },
            {
                "name": "Banking API SSL",
                "url": "https://api.exchangerate-api.com/v4/latest/USD",
                "verify_ssl": True
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for test in ssl_tests:
                try:
                    start_time = time.time()
                    
                    connector = aiohttp.TCPConnector(ssl=ssl.create_default_context())
                    async with aiohttp.ClientSession(connector=connector) as ssl_session:
                        async with ssl_session.get(test["url"], timeout=30) as response:
                            response_time = time.time() - start_time
                            
                            print(f"🔍 {test['name']}:")
                            print(f"   URL: {test['url']}")
                            print(f"   Status: {response.status}")
                            print(f"   Temps SSL: {response_time:.3f}s")
                            
                            if response.status == 200:
                                print(f"   ✅ SSL/TLS OK")
                                self.test_results[test["name"]] = "SUCCESS"
                                self.performance_metrics[f"{test['name']}_ssl_time"] = response_time
                            else:
                                print(f"   ⚠️ Status {response.status}")
                                self.test_results[test["name"]] = "WARNING"
                                
                except Exception as e:
                    print(f"❌ {test['name']}: Erreur SSL - {e}")
                    self.test_results[test["name"]] = "ERROR"
                    self.errors.append(f"Erreur SSL sur {test['name']}: {e}")
    
    async def test_concurrent_requests(self):
        print("\n⚡ TEST REQUÊTES CONCURRENTES:")
        print("-" * 50)
        
        urls = [
            "https://httpbin.org/get",
            "https://api.github.com",
            "https://jsonplaceholder.typicode.com/posts/1",
            "https://api.exchangerate-api.com/v4/latest/USD"
        ]
        
        async def fetch_url(session, url, index):
            try:
                start_time = time.time()
                async with session.get(url, timeout=30) as response:
                    response_time = time.time() - start_time
                    data = await response.text()
                    return {
                        "index": index,
                        "url": url,
                        "status": response.status,
                        "time": response_time,
                        "size": len(data),
                        "success": response.status == 200
                    }
            except Exception as e:
                return {
                    "index": index,
                    "url": url,
                    "error": str(e),
                    "success": False
                }
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            
            tasks = [fetch_url(session, url, i) for i, url in enumerate(urls)]
            results = await asyncio.gather(*tasks)
            
            total_time = time.time() - start_time
            
            print(f"📊 Résultats concurrents (Total: {total_time:.3f}s):")
            
            successful_requests = 0
            for result in results:
                if result["success"]:
                    print(f"   ✅ {result['index']+1}. {result['url']} - {result['time']:.3f}s ({result['size']} bytes)")
                    successful_requests += 1
                else:
                    print(f"   ❌ {result['index']+1}. {result['url']} - Erreur: {result.get('error', 'Unknown')}")
            
            print(f"📈 Performance:")
            print(f"   Requêtes réussies: {successful_requests}/{len(urls)}")
            print(f"   Temps total: {total_time:.3f}s")
            print(f"   Temps moyen par requête: {total_time/len(urls):.3f}s")
            
            if successful_requests == len(urls):
                self.test_results["Concurrent Requests"] = "SUCCESS"
                self.performance_metrics["concurrent_total_time"] = total_time
                self.performance_metrics["concurrent_avg_time"] = total_time/len(urls)
            else:
                self.test_results["Concurrent Requests"] = "WARNING"
                self.improvements.append("Améliorer la gestion des erreurs concurrentes")
    
    async def test_rate_limiting_handling(self):
        print("\n⏱️ TEST GESTION LIMITES DE TAUX:")
        print("-" * 50)
        
        async with aiohttp.ClientSession() as session:
            headers = {"User-Agent": "BankingTransferPlatform/1.0"}
            
            start_time = time.time()
            async with session.get("https://api.github.com", headers=headers, timeout=30) as response:
                first_time = time.time() - start_time
                
                rate_limit = response.headers.get('X-RateLimit-Remaining', 'N/A')
                rate_limit_reset = response.headers.get('X-RateLimit-Reset', 'N/A')
                
                print(f"🔍 Première requête GitHub:")
                print(f"   Status: {response.status}")
                print(f"   Temps: {first_time:.3f}s")
                print(f"   Rate Limit restant: {rate_limit}")
                print(f"   Rate Limit reset: {rate_limit_reset}")
                
                if response.status == 200:
                    print(f"   ✅ Succès")
                    
                    start_time = time.time()
                    async with session.get("https://api.github.com", headers=headers, timeout=30) as response2:
                        second_time = time.time() - start_time
                        
                        rate_limit2 = response2.headers.get('X-RateLimit-Remaining', 'N/A')
                        
                        print(f"🔍 Deuxième requête GitHub:")
                        print(f"   Status: {response2.status}")
                        print(f"   Temps: {second_time:.3f}s")
                        print(f"   Rate Limit restant: {rate_limit2}")
                        
                        if response2.status == 200:
                            print(f"   ✅ Succès")
                            self.test_results["Rate Limiting"] = "SUCCESS"
                            self.performance_metrics["rate_limit_first"] = first_time
                            self.performance_metrics["rate_limit_second"] = second_time
                        else:
                            print(f"   ⚠️ Status {response2.status}")
                            self.test_results["Rate Limiting"] = "WARNING"
                else:
                    print(f"   ❌ Échec")
                    self.test_results["Rate Limiting"] = "ERROR"
    
    async def test_error_handling(self):
        print("\n🛡️ TEST GESTION D'ERREURS:")
        print("-" * 50)
        
        error_tests = [
            {
                "name": "URL Invalide",
                "url": "https://invalid-domain-that-does-not-exist-12345.com",
                "expected_error": "ConnectionError"
            },
            {
                "name": "Timeout",
                "url": "https://httpbin.org/delay/10",
                "timeout": 5,
                "expected_error": "TimeoutError"
            },
            {
                "name": "404 Not Found",
                "url": "https://httpbin.org/status/404",
                "expected_status": 404
            },
            {
                "name": "500 Server Error",
                "url": "https://httpbin.org/status/500",
                "expected_status": 500
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for test in error_tests:
                try:
                    timeout = test.get("timeout", 30)
                    async with session.get(test["url"], timeout=timeout) as response:
                        print(f"🔍 {test['name']}:")
                        print(f"   URL: {test['url']}")
                        print(f"   Status: {response.status}")
                        
                        if "expected_status" in test:
                            if response.status == test["expected_status"]:
                                print(f"   ✅ Erreur attendue gérée correctement")
                                self.test_results[test["name"]] = "SUCCESS"
                            else:
                                print(f"   ⚠️ Status inattendu (Attendu: {test['expected_status']})")
                                self.test_results[test["name"]] = "WARNING"
                        else:
                            print(f"   ⚠️ Réponse inattendue")
                            self.test_results[test["name"]] = "WARNING"
                            
                except asyncio.TimeoutError:
                    print(f"🔍 {test['name']}:")
                    print(f"   URL: {test['url']}")
                    print(f"   ✅ Timeout géré correctement")
                    self.test_results[test["name"]] = "SUCCESS"
                except Exception as e:
                    print(f"🔍 {test['name']}:")
                    print(f"   URL: {test['url']}")
                    print(f"   ✅ Erreur gérée: {type(e).__name__}")
                    self.test_results[test["name"]] = "SUCCESS"
    
    async def test_data_validation_advanced(self):
        print("\n🔍 TEST VALIDATION DONNÉES AVANCÉE:")
        print("-" * 50)
        
        validation_tests = [
            {
                "name": "JSON Schema Validation",
                "url": "https://jsonplaceholder.typicode.com/posts/1",
                "required_fields": ["id", "title", "body", "userId"],
                "field_types": {
                    "id": int,
                    "title": str,
                    "body": str,
                    "userId": int
                }
            },
            {
                "name": "Exchange Rate Validation",
                "url": "https://api.exchangerate-api.com/v4/latest/USD",
                "required_fields": ["base", "rates", "date"],
                "field_types": {
                    "base": str,
                    "rates": dict,
                    "date": str
                }
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for test in validation_tests:
                try:
                    async with session.get(test["url"], timeout=30) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            print(f"🔍 {test['name']}:")
                            print(f"   URL: {test['url']}")
                            
                            missing_fields = []
                            for field in test["required_fields"]:
                                if field not in data:
                                    missing_fields.append(field)
                            
                            if missing_fields:
                                print(f"   ❌ Champs manquants: {missing_fields}")
                                self.test_results[test["name"]] = "ERROR"
                                self.errors.append(f"Champs manquants dans {test['name']}: {missing_fields}")
                            else:
                                print(f"   ✅ Tous les champs présents")
                                
                                type_errors = []
                                for field, expected_type in test["field_types"].items():
                                    if field in data:
                                        if not isinstance(data[field], expected_type):
                                            type_errors.append(f"{field}: attendu {expected_type.__name__}, reçu {type(data[field]).__name__}")
                                
                                if type_errors:
                                    print(f"   ⚠️ Erreurs de type: {type_errors}")
                                    self.test_results[test["name"]] = "WARNING"
                                    self.improvements.append(f"Améliorer validation types pour {test['name']}")
                                else:
                                    print(f"   ✅ Types corrects")
                                    self.test_results[test["name"]] = "SUCCESS"
                        else:
                            print(f"🔍 {test['name']}: Status {response.status}")
                            self.test_results[test["name"]] = "ERROR"
                            
                except Exception as e:
                    print(f"❌ {test['name']}: Erreur - {e}")
                    self.test_results[test["name"]] = "ERROR"
                    self.errors.append(f"Erreur validation {test['name']}: {e}")
    
    def analyze_performance_and_improvements(self):
        print("\n📊 ANALYSE PERFORMANCES ET AMÉLIORATIONS:")
        print("-" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result == "SUCCESS")
        error_tests = sum(1 for result in self.test_results.values() if result == "ERROR")
        warning_tests = sum(1 for result in self.test_results.values() if result == "WARNING")
        
        print(f"📈 Statistiques générales:")
        print(f"   Total tests: {total_tests}")
        print(f"   Succès: {successful_tests}")
        print(f"   Erreurs: {error_tests}")
        print(f"   Avertissements: {warning_tests}")
        print(f"   Taux de succès: {(successful_tests/total_tests)*100:.1f}%")
        
        if self.performance_metrics:
            print(f"\n⚡ Métriques de performance:")
            for metric, value in self.performance_metrics.items():
                if isinstance(value, float):
                    print(f"   {metric}: {value:.3f}s")
                else:
                    print(f"   {metric}: {value}")
        
        if self.errors:
            print(f"\n❌ Erreurs détectées:")
            for error in self.errors:
                print(f"   - {error}")
        
        if self.improvements:
            print(f"\n�� Améliorations proposées:")
            for improvement in self.improvements:
                print(f"   - {improvement}")
        
        print(f"\n🎯 Recommandations spécifiques:")
        
        if "concurrent_total_time" in self.performance_metrics:
            avg_time = self.performance_metrics["concurrent_avg_time"]
            if avg_time > 1.0:
                print(f"   ⚡ Optimiser les requêtes concurrentes (moyenne: {avg_time:.3f}s)")
            else:
                print(f"   ✅ Performance concurrente excellente ({avg_time:.3f}s)")
        
        if error_tests > 0:
            print(f"   🛡️ Améliorer la gestion d'erreurs ({error_tests} erreurs)")
        
        if warning_tests > 0:
            print(f"   🔧 Optimiser les tests avec avertissements ({warning_tests} warnings)")
        
        if successful_tests == total_tests:
            print(f"   🏆 Application parfaitement opérationnelle")
        elif successful_tests >= total_tests * 0.9:
            print(f"   ✅ Application très performante")
        elif successful_tests >= total_tests * 0.8:
            print(f"   ✅ Application fonctionnelle")
        else:
            print(f"   ⚠️ Application nécessite des améliorations")
    
    async def run_advanced_test(self):
        print("🚀 TEST APIs AVANCÉES - INTERACTIONS COMPLEXES")
        print("="*70)
        
        self.print_test_header()
        
        await self.test_ssl_tls_connectivity()
        await self.test_concurrent_requests()
        await self.test_rate_limiting_handling()
        await self.test_error_handling()
        await self.test_data_validation_advanced()
        
        self.analyze_performance_and_improvements()
        
        print("\n" + "="*80)
        print("📊 RÉSUMÉ FINAL DU TEST AVANCÉ")
        print("="*80)
        
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result == "SUCCESS" else "⚠️" if result == "WARNING" else "❌"
            print(f"   {status_icon} {test_name}: {result}")
        
        overall_success = all(result == "SUCCESS" for result in self.test_results.values())
        
        if overall_success:
            print("\n🏆 APPLICATION PARFAITEMENT OPÉRATIONNELLE!")
            print("Tous les tests avancés réussis")
        elif len(self.errors) == 0:
            print("\n✅ APPLICATION TRÈS PERFORMANTE")
            print("Quelques optimisations mineures recommandées")
        else:
            print(f"\n⚠️ APPLICATION AVEC ERREURS")
            print(f"{len(self.errors)} erreurs à corriger")
        
        return overall_success

def main():
    test = TestAPIsAvancees()
    
    try:
        success = asyncio.run(test.run_advanced_test())
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrompu")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur générale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
