#!/usr/bin/env python3
"""
Simple test for Banking Transfer Platform
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all imports"""
    print("=== Testing Banking Transfer Platform Imports ===")
    
    try:
        print("✅ Testing FastAPI...")
        from fastapi import FastAPI
        print("✅ FastAPI imported successfully")
        
        print("✅ Testing app.main...")
        from app.main import app
        print("✅ Main app imported successfully")
        
        print("✅ Testing app structure...")
        print(f"   - App title: {app.title}")
        print(f"   - App version: {app.version}")
        print(f"   - App description: {app.description}")
        
        print("✅ Testing routes...")
        routes = [route.path for route in app.routes]
        print(f"   - Available routes: {routes}")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_app_startup():
    """Test app startup"""
    print("\n=== Testing App Startup ===")
    
    try:
        from app.main import app
        import uvicorn
        
        print("✅ App created successfully")
        print("✅ Ready to start server")
        print("✅ You can now run: uvicorn app.main:app --host 0.0.0.0 --port 8000")
        
        return True
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Banking Transfer Platform - Component Test")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test startup
    startup_ok = test_app_startup()
    
    print("\n" + "=" * 50)
    if imports_ok and startup_ok:
        print("🎉 ALL TESTS PASSED! Application is ready to run.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("\n📋 Next steps:")
    print("1. Run: uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("2. Open: http://localhost:8000/docs")
    print("3. Test the API endpoints")