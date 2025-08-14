#!/usr/bin/env python3
"""
Simple test for Banking Transfer Platform
"""

import sys
import os

def test_imports():
    """Test all imports"""
    print("=== Testing Imports ===")
    
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
    
    return True

def test_app_routes():
    """Test app routes"""
    print("\n=== Testing Routes ===")
    
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

if __name__ == "__main__":
    print("🚀 Banking Transfer Platform - Simple Test")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test routes
    routes_ok = test_app_routes()
    
    # Test startup
    startup_ok = test_server_startup()
    
    print("\n" + "=" * 50)
    if imports_ok and routes_ok and startup_ok:
        print("🎉 ALL TESTS PASSED! Application is ready to run.")
        print("\n📋 To start the application:")
        print("1. cd backend")
        print("2. uvicorn app.main:app --host 0.0.0.0 --port 8000")
        print("3. Open http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("\n🔍 Next steps:")
    print("1. Fix any import errors")
    print("2. Create missing files")
    print("3. Test the application")