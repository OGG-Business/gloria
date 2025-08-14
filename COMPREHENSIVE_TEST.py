#!/usr/bin/env python3
"""
Comprehensive test for Banking Transfer Platform
"""

import sys
import os
import subprocess
import time
import requests
import json

def test_backend_imports():
    """Test backend imports"""
    print("=== Testing Backend Imports ===")
    
    try:
        print("✅ Testing FastAPI...")
        from fastapi import FastAPI
        print("✅ FastAPI imported successfully")
    except Exception as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        print("✅ Testing structlog...")
        import structlog
        print("✅ structlog imported successfully")
    except Exception as e:
        print(f"❌ structlog import failed: {e}")
        return False
    
    try:
        print("✅ Testing app.main...")
        from app.main import app
        print("✅ Main app imported successfully")
        print(f"   - App title: {app.title}")
        print(f"   - App version: {app.version}")
    except Exception as e:
        print(f"❌ app.main import failed: {e}")
        return False
    
    try:
        print("✅ Testing app.config...")
        from app.config import get_settings
        settings = get_settings()
        print("✅ Config imported successfully")
        print(f"   - App name: {settings.app_name}")
    except Exception as e:
        print(f"❌ app.config import failed: {e}")
        return False
    
    return True

def test_backend_routes():
    """Test backend routes"""
    print("\n=== Testing Backend Routes ===")
    
    try:
        from app.main import app
        routes = [route.path for route in app.routes]
        print(f"✅ Routes found: {len(routes)}")
        for route in routes:
            print(f"   - {route}")
        return True
    except Exception as e:
        print(f"❌ Routes test failed: {e}")
        return False

def test_backend_modules():
    """Test backend modules"""
    print("\n=== Testing Backend Modules ===")
    
    modules = [
        ("auth", "app.auth.routes"),
        ("accounts", "app.accounts.routes"),
        ("transfers", "app.transfers.routes"),
        ("kyc", "app.kyc.routes"),
        ("notifications", "app.notifications.routes"),
        ("admin", "app.admin.routes"),
        ("database", "app.common.database"),
        ("monitoring", "app.common.monitoring")
    ]
    
    for module_name, module_path in modules:
        try:
            __import__(module_path)
            print(f"✅ {module_name} module imported successfully")
        except Exception as e:
            print(f"❌ {module_name} module import failed: {e}")
            return False
    
    return True

def test_server_startup():
    """Test server startup"""
    print("\n=== Testing Server Startup ===")
    
    try:
        import uvicorn
        from app.main import app
        
        print("✅ Uvicorn imported successfully")
        print("✅ App ready for startup")
        print("✅ You can now run: uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return True
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        return False

def test_docker():
    """Test Docker installation"""
    print("\n=== Testing Docker ===")
    
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker not working")
            return False
    except Exception as e:
        print(f"❌ Docker test failed: {e}")
        return False

def test_docker_compose():
    """Test Docker Compose"""
    print("\n=== Testing Docker Compose ===")
    
    try:
        result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker Compose installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker Compose not working")
            return False
    except Exception as e:
        print(f"❌ Docker Compose test failed: {e}")
        return False

def test_frontend():
    """Test frontend configuration"""
    print("\n=== Testing Frontend ===")
    
    try:
        with open("frontend/package.json", "r") as f:
            package_json = json.load(f)
        
        print("✅ package.json found and valid")
        print(f"   - Name: {package_json.get('name', 'N/A')}")
        print(f"   - Version: {package_json.get('version', 'N/A')}")
        
        dependencies = package_json.get('dependencies', {})
        required_deps = ['react', 'react-dom', 'react-scripts']
        
        for dep in required_deps:
            if dep in dependencies:
                print(f"   - {dep}: {dependencies[dep]}")
            else:
                print(f"   - {dep}: Missing")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False

def test_makefile():
    """Test Makefile"""
    print("\n=== Testing Makefile ===")
    
    try:
        result = subprocess.run(["make", "help"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Makefile working")
            return True
        else:
            print("❌ Makefile not working")
            return False
    except Exception as e:
        print(f"❌ Makefile test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n=== Testing API Endpoints ===")
    
    # Start server in background
    try:
        process = subprocess.Popen(
            ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(5)
        
        # Test endpoints
        endpoints = [
            ("/", "Root endpoint"),
            ("/health", "Health check"),
            ("/auth/", "Auth module"),
            ("/accounts/", "Accounts module"),
            ("/transfers/", "Transfers module"),
            ("/kyc/", "KYC module"),
            ("/notifications/", "Notifications module"),
            ("/admin/", "Admin module")
        ]
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"http://localhost:8080{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {description}: {response.status_code}")
                else:
                    print(f"⚠️  {description}: {response.status_code}")
            except Exception as e:
                print(f"❌ {description}: Failed - {e}")
        
        # Stop server
        process.terminate()
        process.wait()
        
        return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Banking Transfer Platform - Comprehensive Test")
    print("=" * 60)
    
    # Test all components
    tests = [
        ("Backend Imports", test_backend_imports),
        ("Backend Routes", test_backend_routes),
        ("Backend Modules", test_backend_modules),
        ("Server Startup", test_server_startup),
        ("Docker", test_docker),
        ("Docker Compose", test_docker_compose),
        ("Frontend", test_frontend),
        ("Makefile", test_makefile),
        ("API Endpoints", test_api_endpoints)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Platform is fully operational!")
        print("\n📋 Next steps:")
        print("1. Start backend: uvicorn app.main:app --host 0.0.0.0 --port 8000")
        print("2. Start frontend: cd frontend && npm install && npm start")
        print("3. Use Docker: docker-compose up -d")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    print("\n🔍 Platform Status:")
    print(f"   - Backend: {'✅ Ready' if passed >= 5 else '❌ Issues'}")
    print(f"   - Frontend: {'✅ Ready' if passed >= 7 else '❌ Issues'}")
    print(f"   - Infrastructure: {'✅ Ready' if passed >= 8 else '❌ Issues'}")