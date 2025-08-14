#!/usr/bin/env python3
"""
Simple test script for Banking Transfer Platform
Tests basic functionality without complex dependencies
"""

import os
import sys
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def test_basic_structure():
    """Test basic project structure"""
    print_header("Testing Basic Project Structure")
    
    # Check if we're in the right directory
    if not Path("backend").exists():
        print_error("Backend directory not found")
        return False
    
    if not Path("frontend").exists():
        print_error("Frontend directory not found")
        return False
    
    print_success("Project structure found")
    
    # Check existing files
    existing_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(('.py', '.yml', '.yaml', '.json', '.md')):
                file_path = os.path.join(root, file)
                existing_files.append(file_path)
    
    print_info(f"Found {len(existing_files)} files")
    
    # Show some key files
    key_files = [
        "docker-compose.yml",
        "Makefile",
        "backend/app/transfers/routes.py",
        "backend/app/transfers/services.py",
        "backend/app/accounts/routes.py"
    ]
    
    for file_path in key_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            print_success(f"Found {file_path} ({size} bytes)")
        else:
            print_error(f"Missing {file_path}")
    
    return True

def test_python_syntax():
    """Test Python syntax for existing files"""
    print_header("Testing Python Syntax")
    
    python_files = []
    for root, dirs, files in os.walk("backend"):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    if not python_files:
        print_error("No Python files found in backend")
        return False
    
    print_info(f"Found {len(python_files)} Python files")
    
    syntax_errors = []
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                compile(f.read(), file_path, 'exec')
            print_success(f"Syntax OK: {file_path}")
        except SyntaxError as e:
            syntax_errors.append((file_path, str(e)))
            print_error(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            syntax_errors.append((file_path, str(e)))
            print_error(f"Error in {file_path}: {e}")
    
    if syntax_errors:
        print_error(f"Found {len(syntax_errors)} syntax errors")
        return False
    else:
        print_success("All Python files have valid syntax")
        return True

def test_docker_compose():
    """Test Docker Compose configuration"""
    print_header("Testing Docker Compose")
    
    try:
        import yaml
        
        with open("docker-compose.yml", "r") as f:
            compose_config = yaml.safe_load(f)
        
        # Check required services
        required_services = ["postgres", "redis", "backend", "frontend"]
        for service in required_services:
            if service in compose_config["services"]:
                print_success(f"Service {service} found")
            else:
                print_error(f"Service {service} missing")
                return False
        
        print_success("Docker Compose configuration valid")
        return True
        
    except Exception as e:
        print_error(f"Docker Compose test failed: {e}")
        return False

def test_makefile():
    """Test Makefile"""
    print_header("Testing Makefile")
    
    try:
        with open("Makefile", "r") as f:
            makefile_content = f.read()
        
        # Check for required targets
        required_targets = ["help", "build", "up", "down"]
        for target in required_targets:
            if f"{target}:" in makefile_content:
                print_success(f"Target {target} found")
            else:
                print_error(f"Target {target} missing")
                return False
        
        print_success("Makefile is valid")
        return True
        
    except Exception as e:
        print_error(f"Makefile test failed: {e}")
        return False

def test_file_contents():
    """Test content of key files"""
    print_header("Testing File Contents")
    
    # Test docker-compose.yml
    try:
        with open("docker-compose.yml", "r") as f:
            content = f.read()
            if "version:" in content and "services:" in content:
                print_success("docker-compose.yml has valid content")
            else:
                print_error("docker-compose.yml content invalid")
                return False
    except Exception as e:
        print_error(f"Error reading docker-compose.yml: {e}")
        return False
    
    # Test Makefile
    try:
        with open("Makefile", "r") as f:
            content = f.read()
            if "help:" in content and "build:" in content:
                print_success("Makefile has valid content")
            else:
                print_error("Makefile content invalid")
                return False
    except Exception as e:
        print_error(f"Error reading Makefile: {e}")
        return False
    
    # Test backend files
    backend_files = [
        "backend/app/transfers/routes.py",
        "backend/app/transfers/services.py",
        "backend/app/accounts/routes.py"
    ]
    
    for file_path in backend_files:
        try:
            with open(file_path, "r") as f:
                content = f.read()
                if len(content) > 100:  # Should have substantial content
                    print_success(f"{file_path} has content ({len(content)} chars)")
                else:
                    print_error(f"{file_path} has insufficient content")
                    return False
        except Exception as e:
            print_error(f"Error reading {file_path}: {e}")
            return False
    
    return True

def main():
    """Main test function"""
    print_header("Banking Transfer Platform - Simple Test")
    
    tests = [
        ("Basic Structure", test_basic_structure),
        ("Python Syntax", test_python_syntax),
        ("Docker Compose", test_docker_compose),
        ("Makefile", test_makefile),
        ("File Contents", test_file_contents),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("All basic tests passed!")
        print_info("The platform has a solid foundation.")
        print_info("Next steps:")
        print_info("1. Install Python dependencies")
        print_info("2. Create missing backend files")
        print_info("3. Set up frontend")
        print_info("4. Run docker-compose up")
        return True
    else:
        print_error(f"{total - passed} tests failed.")
        print_info("Please fix the issues above before proceeding.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_info("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Test failed with unexpected error: {e}")
        sys.exit(1)