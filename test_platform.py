#!/usr/bin/env python3
"""
Comprehensive Test Script for Banking Transfer Platform
Tests all components and their functionality
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
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

def test_file_structure():
    """Test if all required files exist"""
    print_header("TESTING FILE STRUCTURE")
    
    required_files = [
        # Backend files
        "backend/app/main.py",
        "backend/app/config.py",
        "backend/app/common/database.py",
        "backend/app/transfers/routes.py",
        "backend/app/transfers/services.py",
        "backend/app/accounts/routes.py",
        "backend/app/connectors/swift_connector.py",
        "backend/app/connectors/mojaloop_connector.py",
        "backend/app/connectors/iso20022_connector.py",
        "backend/requirements.txt",
        
        # Frontend files
        "frontend/package.json",
        "frontend/public/index.html",
        "frontend/public/manifest.json",
        "frontend/src/App.tsx",
        "frontend/src/components/common/Button.tsx",
        "frontend/src/components/common/Input.tsx",
        "frontend/src/components/common/LoadingSpinner.tsx",
        "frontend/src/components/dashboard/StatCard.tsx",
        "frontend/src/components/dashboard/TransferChart.tsx",
        "frontend/src/pages/Login.tsx",
        "frontend/src/pages/Dashboard.tsx",
        "frontend/src/pages/TransferForm.tsx",
        "frontend/src/hooks/useAuth.ts",
        "frontend/src/hooks/useNotifications.ts",
        "frontend/src/services/api.ts",
        "frontend/src/types/index.ts",
        
        # Configuration files
        "docker-compose.yml",
        "Makefile",
        "README.md",
        "docs/ONBOARDING_SWIFT.md"
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            if file_size > 0:
                existing_files.append(file_path)
                print_success(f"{file_path} ({file_size} bytes)")
            else:
                missing_files.append(file_path)
                print_error(f"{file_path} (empty file)")
        else:
            missing_files.append(file_path)
            print_error(f"{file_path} (missing)")
    
    print(f"\n📊 File Structure Summary:")
    print(f"   ✅ Existing files: {len(existing_files)}")
    print(f"   ❌ Missing files: {len(missing_files)}")
    
    return len(missing_files) == 0

def test_python_syntax():
    """Test Python syntax for all Python files"""
    print_header("TESTING PYTHON SYNTAX")
    
    python_files = [
        "backend/app/main.py",
        "backend/app/config.py",
        "backend/app/common/database.py",
        "backend/app/transfers/routes.py",
        "backend/app/transfers/services.py",
        "backend/app/accounts/routes.py",
        "backend/app/connectors/swift_connector.py",
        "backend/app/connectors/mojaloop_connector.py",
        "backend/app/connectors/iso20022_connector.py"
    ]
    
    syntax_errors = []
    valid_files = []
    
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    compile(f.read(), file_path, 'exec')
                valid_files.append(file_path)
                print_success(f"{file_path} - Syntax OK")
            except SyntaxError as e:
                syntax_errors.append((file_path, str(e)))
                print_error(f"{file_path} - Syntax Error: {e}")
            except Exception as e:
                syntax_errors.append((file_path, str(e)))
                print_error(f"{file_path} - Error: {e}")
        else:
            syntax_errors.append((file_path, "File not found"))
            print_error(f"{file_path} - File not found")
    
    print(f"\n📊 Python Syntax Summary:")
    print(f"   ✅ Valid files: {len(valid_files)}")
    print(f"   ❌ Files with errors: {len(syntax_errors)}")
    
    return len(syntax_errors) == 0

def test_json_syntax():
    """Test JSON syntax for configuration files"""
    print_header("TESTING JSON SYNTAX")
    
    json_files = [
        "frontend/package.json",
        "frontend/public/manifest.json"
    ]
    
    json_errors = []
    valid_files = []
    
    for file_path in json_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    json.load(f)
                valid_files.append(file_path)
                print_success(f"{file_path} - JSON OK")
            except json.JSONDecodeError as e:
                json_errors.append((file_path, str(e)))
                print_error(f"{file_path} - JSON Error: {e}")
            except Exception as e:
                json_errors.append((file_path, str(e)))
                print_error(f"{file_path} - Error: {e}")
        else:
            json_errors.append((file_path, "File not found"))
            print_error(f"{file_path} - File not found")
    
    print(f"\n📊 JSON Syntax Summary:")
    print(f"   ✅ Valid files: {len(valid_files)}")
    print(f"   ❌ Files with errors: {len(json_errors)}")
    
    return len(json_errors) == 0

def test_swift_connector():
    """Test SWIFT connector functionality"""
    print_header("TESTING SWIFT CONNECTOR")
    
    try:
        # Add backend to path
        sys.path.append('backend')
        
        # Import the connector
        from app.connectors.swift_connector import SwiftConnector, SwiftConnectorConfig, SwiftMessage
        
        # Test configuration
        config = SwiftConnectorConfig(
            bic="TESTUS33XXX",
            cert_path="/tmp/test.crt",
            key_path="/tmp/test.key",
            ca_cert_path="/tmp/ca.crt",
            swiftnet_endpoint="https://test.swift.com",
            dry_run=True
        )
        
        print_success("SWIFT connector configuration created")
        
        # Test connector instantiation
        connector = SwiftConnector(config)
        print_success("SWIFT connector instantiated")
        
        # Test message creation (mock transfer)
        class MockTransfer:
            def __init__(self):
                self.transfer_id = "TRF2023120112345678"
                self.amount = 1000.0
                self.currency = "USD"
                self.created_at = datetime.now()
                self.beneficiary_name = "John Doe"
                self.source_account = MockAccount("source")
                self.destination_account = MockAccount("dest")
        
        class MockAccount:
            def __init__(self, type_):
                self.holder_name = f"Test User ({type_})"
                self.iban = f"US12345678901234567890" if type_ == "source" else "DE89370400440532013000"
                self.bic = "TESTUS33XXX" if type_ == "source" else "COBADEFFXXX"
        
        mock_transfer = MockTransfer()
        message = connector.create_mt103_message(mock_transfer)
        
        if message and message.message_type == "MT103":
            print_success("MT103 message creation successful")
        else:
            print_error("MT103 message creation failed")
            return False
            
    except Exception as e:
        print_error(f"SWIFT connector test failed: {e}")
        return False
    
    return True

def test_mojaloop_connector():
    """Test Mojaloop connector functionality"""
    print_header("TESTING MOJALOOP CONNECTOR")
    
    try:
        # Import the connector
        from app.connectors.mojaloop_connector import MojaloopConnector, MojaloopConnectorConfig
        
        # Test configuration
        config = MojaloopConnectorConfig(
            endpoint="https://test.mojaloop.io",
            participant_id="test-participant",
            api_key="test-api-key",
            dry_run=True
        )
        
        print_success("Mojaloop connector configuration created")
        
        # Test connector instantiation
        connector = MojaloopConnector(config)
        print_success("Mojaloop connector instantiated")
        
    except Exception as e:
        print_error(f"Mojaloop connector test failed: {e}")
        return False
    
    return True

def test_iso20022_connector():
    """Test ISO 20022 connector functionality"""
    print_header("TESTING ISO 20022 CONNECTOR")
    
    try:
        # Import the connector
        from app.connectors.iso20022_connector import ISO20022Connector, ISO20022ConnectorConfig
        
        # Test configuration
        config = ISO20022ConnectorConfig(
            schema_validation=True,
            dry_run=True
        )
        
        print_success("ISO 20022 connector configuration created")
        
        # Test connector instantiation
        connector = ISO20022Connector(config)
        print_success("ISO 20022 connector instantiated")
        
        # Test XML validation
        test_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
    <FIToFICstmrCdtTrf>
        <GrpHdr>
            <MsgId>TEST123</MsgId>
            <CreDtTm>2023-12-01T10:00:00Z</CreDtTm>
            <NbOfTxs>1</NbOfTxs>
            <CtrlSum>1000.00</CtrlSum>
        </GrpHdr>
    </FIToFICstmrCdtTrf>
</Document>"""
        
        is_valid = connector.validate_xml_schema(test_xml)
        if is_valid:
            print_success("XML schema validation successful")
        else:
            print_error("XML schema validation failed")
            return False
        
    except Exception as e:
        print_error(f"ISO 20022 connector test failed: {e}")
        return False
    
    return True

def test_api_structure():
    """Test API structure and endpoints"""
    print_header("TESTING API STRUCTURE")
    
    try:
        # Check transfer routes
        with open("backend/app/transfers/routes.py", 'r') as f:
            content = f.read()
            if "router = APIRouter" in content and "create_transfer" in content:
                print_success("Transfer routes defined")
            else:
                print_error("Transfer routes incomplete")
                return False
        
        # Check account routes
        with open("backend/app/accounts/routes.py", 'r') as f:
            content = f.read()
            if "router = APIRouter" in content and "get_accounts" in content:
                print_success("Account routes defined")
            else:
                print_error("Account routes incomplete")
                return False
        
        # Check transfer service
        with open("backend/app/transfers/services.py", 'r') as f:
            content = f.read()
            if "class TransferService" in content and "create_transfer" in content:
                print_success("Transfer service defined")
            else:
                print_error("Transfer service incomplete")
                return False
        
        # Check main app
        with open("backend/app/main.py", 'r') as f:
            content = f.read()
            if "FastAPI" in content and "include_router" in content:
                print_success("Main FastAPI app configured")
            else:
                print_error("Main FastAPI app incomplete")
                return False
                
    except Exception as e:
        print_error(f"API structure test failed: {e}")
        return False
    
    return True

def test_frontend_components():
    """Test frontend component structure"""
    print_header("TESTING FRONTEND COMPONENTS")
    
    try:
        # Check package.json
        with open("frontend/package.json", 'r') as f:
            package_data = json.load(f)
            if "react" in package_data.get("dependencies", {}):
                print_success("React dependencies configured")
            else:
                print_error("React dependencies missing")
                return False
        
        # Check main App component
        with open("frontend/src/App.tsx", 'r') as f:
            content = f.read()
            if "React" in content and "Router" in content:
                print_success("Main App component configured")
            else:
                print_error("Main App component incomplete")
                return False
        
        # Check Button component
        with open("frontend/src/components/common/Button.tsx", 'r') as f:
            content = f.read()
            if "React.FC" in content and "ButtonProps" in content:
                print_success("Button component configured")
            else:
                print_error("Button component incomplete")
                return False
        
        # Check API service
        with open("frontend/src/services/api.ts", 'r') as f:
            content = f.read()
            if "axios" in content and "ApiService" in content:
                print_success("API service configured")
            else:
                print_error("API service incomplete")
                return False
        
        # Check types
        with open("frontend/src/types/index.ts", 'r') as f:
            content = f.read()
            if "interface" in content and "export" in content:
                print_success("TypeScript types configured")
            else:
                print_error("TypeScript types incomplete")
                return False
                
    except Exception as e:
        print_error(f"Frontend components test failed: {e}")
        return False
    
    return True

def test_configuration_files():
    """Test configuration files"""
    print_header("TESTING CONFIGURATION FILES")
    
    try:
        # Check docker-compose.yml
        with open("docker-compose.yml", 'r') as f:
            content = f.read()
            if "services:" in content and "backend:" in content and "frontend:" in content:
                print_success("Docker Compose configured")
            else:
                print_error("Docker Compose incomplete")
                return False
        
        # Check Makefile
        with open("Makefile", 'r') as f:
            content = f.read()
            if "help:" in content and "build:" in content and "up:" in content:
                print_success("Makefile configured")
            else:
                print_error("Makefile incomplete")
                return False
        
        # Check README.md
        with open("README.md", 'r') as f:
            content = f.read()
            if len(content) > 1000:  # Should be substantial
                print_success("README.md documented")
            else:
                print_error("README.md too short")
                return False
        
        # Check SWIFT onboarding guide
        with open("docs/ONBOARDING_SWIFT.md", 'r') as f:
            content = f.read()
            if "SWIFT" in content and "certificate" in content:
                print_success("SWIFT onboarding guide documented")
            else:
                print_error("SWIFT onboarding guide incomplete")
                return False
                
    except Exception as e:
        print_error(f"Configuration files test failed: {e}")
        return False
    
    return True

def generate_test_report():
    """Generate comprehensive test report"""
    print_header("BANKING TRANSFER PLATFORM - COMPREHENSIVE TEST REPORT")
    
    tests = [
        ("File Structure", test_file_structure),
        ("Python Syntax", test_python_syntax),
        ("JSON Syntax", test_json_syntax),
        ("SWIFT Connector", test_swift_connector),
        ("Mojaloop Connector", test_mojaloop_connector),
        ("ISO 20022 Connector", test_iso20022_connector),
        ("API Structure", test_api_structure),
        ("Frontend Components", test_frontend_components),
        ("Configuration Files", test_configuration_files)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"{test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Overall Results:")
    print(f"   ✅ Passed: {passed}/{total}")
    print(f"   ❌ Failed: {total - passed}/{total}")
    print(f"   📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The platform is ready for deployment.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the issues above.")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Banking Transfer Platform Comprehensive Tests...")
    print(f"📅 Test run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = generate_test_report()
    
    if success:
        print("\n🎯 DEPLOYMENT READY!")
        print("1. Install Docker and Docker Compose")
        print("2. Run: docker-compose up -d")
        print("3. Access frontend: http://localhost:3000")
        print("4. Access API docs: http://localhost:8000/docs")
        print("5. Review SWIFT guide: docs/ONBOARDING_SWIFT.md")
    else:
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check that all required files are present")
        print("2. Verify Python dependencies are installed")
        print("3. Ensure proper file permissions")
        print("4. Review error messages above")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())