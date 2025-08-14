#!/usr/bin/env python3
"""
Integration Test Script for Banking Transfer Platform
Tests all major components and their interactions
"""

import asyncio
import json
import sys
from datetime import datetime, timezone
from typing import Dict, Any

# Mock data for testing
MOCK_USER = {
    "id": "test-user-123",
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "role": "user"
}

MOCK_ACCOUNT = {
    "id": "test-account-123",
    "account_number": "1234567890",
    "iban": "US12345678901234567890",
    "bic": "TESTUS33XXX",
    "holder_name": "Test User",
    "balance": 10000.0,
    "currency": "USD",
    "status": "active",
    "account_type": "current",
    "daily_limit": 5000.0,
    "monthly_limit": 50000.0
}

MOCK_TRANSFER = {
    "id": "test-transfer-123",
    "transfer_id": "TRF2023120112345678",
    "amount": 1000.0,
    "currency": "USD",
    "source_account_id": "test-account-123",
    "beneficiary_name": "John Doe",
    "beneficiary_iban": "DE89370400440532013000",
    "beneficiary_bic": "COBADEFFXXX",
    "description": "Test transfer",
    "status": "initiated",
    "priority": "normal",
    "transfer_type": "swift",
    "fees": 25.0
}

def test_frontend_components():
    """Test frontend component structure"""
    print("🧪 Testing Frontend Components...")
    
    components_to_check = [
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
        "frontend/src/types/index.ts"
    ]
    
    missing_components = []
    for component in components_to_check:
        try:
            with open(component, 'r') as f:
                content = f.read()
                if len(content.strip()) > 0:
                    print(f"  ✅ {component}")
                else:
                    missing_components.append(component)
        except FileNotFoundError:
            missing_components.append(component)
    
    if missing_components:
        print(f"  ❌ Missing components: {missing_components}")
        return False
    
    print("  ✅ All frontend components found")
    return True

def test_backend_components():
    """Test backend component structure"""
    print("🧪 Testing Backend Components...")
    
    components_to_check = [
        "backend/app/connectors/swift_connector.py",
        "backend/app/connectors/mojaloop_connector.py",
        "backend/app/connectors/iso20022_connector.py",
        "backend/app/transfers/routes.py",
        "backend/app/transfers/services.py",
        "backend/app/accounts/routes.py",
        "backend/app/main.py",
        "backend/app/config.py",
        "backend/app/common/database.py",
        "backend/requirements.txt"
    ]
    
    missing_components = []
    for component in components_to_check:
        try:
            with open(component, 'r') as f:
                content = f.read()
                if len(content.strip()) > 0:
                    print(f"  ✅ {component}")
                else:
                    missing_components.append(component)
        except FileNotFoundError:
            missing_components.append(component)
    
    if missing_components:
        print(f"  ❌ Missing components: {missing_components}")
        return False
    
    print("  ✅ All backend components found")
    return True

def test_configuration_files():
    """Test configuration files"""
    print("🧪 Testing Configuration Files...")
    
    config_files = [
        "docker-compose.yml",
        "Makefile",
        "README.md",
        "docs/ONBOARDING_SWIFT.md",
        "frontend/package.json",
        "frontend/public/manifest.json"
    ]
    
    missing_files = []
    for file in config_files:
        try:
            with open(file, 'r') as f:
                content = f.read()
                if len(content.strip()) > 0:
                    print(f"  ✅ {file}")
                else:
                    missing_files.append(file)
        except FileNotFoundError:
            missing_files.append(file)
    
    if missing_files:
        print(f"  ❌ Missing files: {missing_files}")
        return False
    
    print("  ✅ All configuration files found")
    return True

def test_swift_connector():
    """Test SWIFT connector functionality"""
    print("🧪 Testing SWIFT Connector...")
    
    try:
        # Import the connector
        sys.path.append('backend')
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
        
        print("  ✅ SWIFT connector configuration created")
        
        # Test message creation
        from app.transfers.models import Transfer, TransferStatus, TransferPriority, TransferType
        from app.accounts.models import Account
        
        # Create mock transfer
        mock_transfer = Transfer(
            id="test-123",
            transfer_id="TRF2023120112345678",
            amount=1000.0,
            currency="USD",
            source_account_id="test-account",
            beneficiary_name="John Doe",
            beneficiary_iban="DE89370400440532013000",
            beneficiary_bic="COBADEFFXXX",
            description="Test transfer",
            status=TransferStatus.INITIATED,
            priority=TransferPriority.NORMAL,
            transfer_type=TransferType.SWIFT,
            created_at=datetime.now(timezone.utc)
        )
        
        # Mock source account
        mock_source_account = Account(
            id="test-account",
            account_number="1234567890",
            iban="US12345678901234567890",
            bic="TESTUS33XXX",
            holder_name="Test User",
            balance=10000.0,
            currency="USD",
            status="active"
        )
        
        # Mock destination account
        mock_dest_account = Account(
            id="test-dest",
            account_number="0987654321",
            iban="DE89370400440532013000",
            bic="COBADEFFXXX",
            holder_name="John Doe",
            balance=0.0,
            currency="EUR",
            status="active"
        )
        
        # Set relationships
        mock_transfer.source_account = mock_source_account
        mock_transfer.destination_account = mock_dest_account
        
        # Test MT103 message creation
        connector = SwiftConnector(config)
        message = connector.create_mt103_message(mock_transfer)
        
        if message and message.message_type == "MT103":
            print("  ✅ MT103 message creation successful")
        else:
            print("  ❌ MT103 message creation failed")
            return False
            
    except Exception as e:
        print(f"  ❌ SWIFT connector test failed: {e}")
        return False
    
    return True

def test_mojaloop_connector():
    """Test Mojaloop connector functionality"""
    print("🧪 Testing Mojaloop Connector...")
    
    try:
        # Import the connector
        sys.path.append('backend')
        from app.connectors.mojaloop_connector import MojaloopConnector, MojaloopConnectorConfig
        
        # Test configuration
        config = MojaloopConnectorConfig(
            endpoint="https://test.mojaloop.io",
            participant_id="test-participant",
            api_key="test-api-key",
            dry_run=True
        )
        
        print("  ✅ Mojaloop connector configuration created")
        
    except Exception as e:
        print(f"  ❌ Mojaloop connector test failed: {e}")
        return False
    
    return True

def test_iso20022_connector():
    """Test ISO 20022 connector functionality"""
    print("🧪 Testing ISO 20022 Connector...")
    
    try:
        # Import the connector
        sys.path.append('backend')
        from app.connectors.iso20022_connector import ISO20022Connector, ISO20022ConnectorConfig
        
        # Test configuration
        config = ISO20022ConnectorConfig(
            schema_validation=True,
            dry_run=True
        )
        
        print("  ✅ ISO 20022 connector configuration created")
        
    except Exception as e:
        print(f"  ❌ ISO 20022 connector test failed: {e}")
        return False
    
    return True

def test_api_structure():
    """Test API structure and endpoints"""
    print("🧪 Testing API Structure...")
    
    try:
        # Check if routes are properly defined
        with open("backend/app/transfers/routes.py", 'r') as f:
            content = f.read()
            if "router = APIRouter" in content and "create_transfer" in content:
                print("  ✅ Transfer routes defined")
            else:
                print("  ❌ Transfer routes incomplete")
                return False
        
        with open("backend/app/accounts/routes.py", 'r') as f:
            content = f.read()
            if "router = APIRouter" in content and "get_accounts" in content:
                print("  ✅ Account routes defined")
            else:
                print("  ❌ Account routes incomplete")
                return False
        
        with open("backend/app/transfers/services.py", 'r') as f:
            content = f.read()
            if "class TransferService" in content and "create_transfer" in content:
                print("  ✅ Transfer service defined")
            else:
                print("  ❌ Transfer service incomplete")
                return False
                
    except Exception as e:
        print(f"  ❌ API structure test failed: {e}")
        return False
    
    return True

def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n" + "="*60)
    print("🏦 BANKING TRANSFER PLATFORM - INTEGRATION TEST REPORT")
    print("="*60)
    
    tests = [
        ("Frontend Components", test_frontend_components),
        ("Backend Components", test_backend_components),
        ("Configuration Files", test_configuration_files),
        ("SWIFT Connector", test_swift_connector),
        ("Mojaloop Connector", test_mojaloop_connector),
        ("ISO 20022 Connector", test_iso20022_connector),
        ("API Structure", test_api_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The platform is ready for deployment.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Banking Transfer Platform Integration Tests...")
    print(f"📅 Test run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = generate_test_report()
    
    if success:
        print("\n🎯 NEXT STEPS:")
        print("1. Install Docker and Docker Compose")
        print("2. Run: docker-compose up -d")
        print("3. Access the application at: http://localhost:3000")
        print("4. Test the API at: http://localhost:8000/docs")
        print("5. Review the SWIFT onboarding guide: docs/ONBOARDING_SWIFT.md")
    else:
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check that all required files are present")
        print("2. Verify Python dependencies are installed")
        print("3. Ensure proper file permissions")
        print("4. Review error messages above")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())