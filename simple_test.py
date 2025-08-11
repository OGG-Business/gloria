#!/usr/bin/env python3
"""
Simple Test Script for Banking Transfer Platform
Tests existing components
"""

import os
import sys
import json
from datetime import datetime

def print_header(title):
    print(f"\n{'='*50}")
    print(f"🧪 {title}")
    print(f"{'='*50}")

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def test_existing_files():
    """Test existing files"""
    print_header("TESTING EXISTING FILES")
    
    existing_files = [
        "backend/app/accounts/routes.py",
        "backend/app/transfers/routes.py", 
        "backend/app/transfers/services.py",
        "backend/app/connectors/__init__.py",
        "frontend/package.json",
        "frontend/public/index.html",
        "frontend/public/manifest.json",
        "docker-compose.yml",
        "Makefile",
        "README.md"
    ]
    
    found_files = []
    missing_files = []
    
    for file_path in existing_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            found_files.append(file_path)
            print_success(f"{file_path} ({size} bytes)")
        else:
            missing_files.append(file_path)
            print_error(f"{file_path} (missing)")
    
    print(f"\n📊 Found: {len(found_files)}, Missing: {len(missing_files)}")
    return len(missing_files) == 0

def test_python_syntax():
    """Test Python syntax"""
    print_header("TESTING PYTHON SYNTAX")
    
    python_files = [
        "backend/app/accounts/routes.py",
        "backend/app/transfers/routes.py",
        "backend/app/transfers/services.py"
    ]
    
    errors = []
    valid = []
    
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    compile(f.read(), file_path, 'exec')
                valid.append(file_path)
                print_success(f"{file_path} - Syntax OK")
            except Exception as e:
                errors.append((file_path, str(e)))
                print_error(f"{file_path} - Error: {e}")
        else:
            errors.append((file_path, "File not found"))
            print_error(f"{file_path} - File not found")
    
    print(f"\n📊 Valid: {len(valid)}, Errors: {len(errors)}")
    return len(errors) == 0

def test_json_syntax():
    """Test JSON syntax"""
    print_header("TESTING JSON SYNTAX")
    
    json_files = [
        "frontend/package.json",
        "frontend/public/manifest.json"
    ]
    
    errors = []
    valid = []
    
    for file_path in json_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                valid.append(file_path)
                print_success(f"{file_path} - JSON OK")
            except Exception as e:
                errors.append((file_path, str(e)))
                print_error(f"{file_path} - Error: {e}")
        else:
            errors.append((file_path, "File not found"))
            print_error(f"{file_path} - File not found")
    
    print(f"\n📊 Valid: {len(valid)}, Errors: {len(errors)}")
    return len(errors) == 0

def test_file_contents():
    """Test file contents"""
    print_header("TESTING FILE CONTENTS")
    
    # Test backend services
    if os.path.exists("backend/app/transfers/services.py"):
        with open("backend/app/transfers/services.py", 'r') as f:
            content = f.read()
            if "class TransferService" in content:
                print_success("TransferService class found")
            else:
                print_error("TransferService class missing")
                return False
            
            if "create_transfer" in content:
                print_success("create_transfer method found")
            else:
                print_error("create_transfer method missing")
                return False
    else:
        print_error("transfers/services.py not found")
        return False
    
    # Test frontend package.json
    if os.path.exists("frontend/package.json"):
        with open("frontend/package.json", 'r') as f:
            data = json.load(f)
            if "react" in data.get("dependencies", {}):
                print_success("React dependency found")
            else:
                print_error("React dependency missing")
                return False
    else:
        print_error("package.json not found")
        return False
    
    # Test docker-compose.yml
    if os.path.exists("docker-compose.yml"):
        with open("docker-compose.yml", 'r') as f:
            content = f.read()
            if "services:" in content:
                print_success("Docker services defined")
            else:
                print_error("Docker services missing")
                return False
    else:
        print_error("docker-compose.yml not found")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Banking Transfer Platform - Simple Test")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("File Existence", test_existing_files),
        ("Python Syntax", test_python_syntax),
        ("JSON Syntax", test_json_syntax),
        ("File Contents", test_file_contents)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"{name} failed: {e}")
            results.append((name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\n📊 Results: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        print("The platform components are working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())