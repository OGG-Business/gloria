#!/usr/bin/env python3
"""
Comprehensive test script for Banking Transfer Platform
Tests all major components and functionality
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section"""
    print(f"\n--- {title} ---")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def test_file_structure():
    """Test if all required files exist"""
    print_header("Testing File Structure")
    
    required_files = [
        "backend/requirements.txt",
        "backend/Dockerfile",
        "backend/app/main.py",
        "backend/app/config.py",
        "backend/app/common/database.py",
        "backend/app/auth/models.py",
        "backend/app/auth/routes.py",
        "backend/app/auth/dependencies.py",
        "backend/app/accounts/models.py",
        "backend/app/accounts/routes.py",
        "backend/app/transfers/models.py",
        "backend/app/transfers/routes.py",
        "backend/app/transfers/services.py",
        "backend/app/kyc/models.py",
        "backend/app/kyc/routes.py",
        "backend/app/audit/models.py",
        "backend/app/notifications/routes.py",
        "backend/app/admin/routes.py",
        "backend/app/connectors/swift_connector.py",
        "backend/app/connectors/mojaloop_connector.py",
        "backend/app/connectors/iso20022_connector.py",
        "docker-compose.yml",
        "Makefile"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"Found {file_path}")
        else:
            print_error(f"Missing {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print_warning(f"Missing {len(missing_files)} files")
        return False
    else:
        print_success("All required files found")
        return True

def test_python_imports():
    """Test if Python modules can be imported"""
    print_header("Testing Python Imports")
    
    try:
        # Test basic imports
        import structlog
        print_success("structlog imported")
        
        import fastapi
        print_success("fastapi imported")
        
        import sqlalchemy
        print_success("sqlalchemy imported")
        
        import pydantic
        print_success("pydantic imported")
        
        # Test app imports
        from app.config import get_settings
        print_success("app.config imported")
        
        from app.common.database import get_db
        print_success("app.common.database imported")
        
        from app.auth.models import User
        print_success("app.auth.models imported")
        
        from app.accounts.models import Account
        print_success("app.accounts.models imported")
        
        from app.transfers.models import Transfer
        print_success("app.transfers.models imported")
        
        from app.kyc.models import KYCDocument
        print_success("app.kyc.models imported")
        
        from app.audit.models import AuditLog
        print_success("app.audit.models imported")
        
        print_success("All Python imports successful")
        return True
        
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return False

def test_connectors():
    """Test connector functionality"""
    print_header("Testing Connectors")
    
    try:
        # Test SWIFT connector
        from app.connectors.swift_connector import SwiftConnector, create_swift_connector
        
        config = {
            "bic": "TESTUS33XXX",
            "endpoint": "https://test.swift.com",
            "dry_run": True
        }
        
        swift_connector = SwiftConnector(config)
        print_success("SWIFT connector created")
        
        # Test Mojaloop connector
        from app.connectors.mojaloop_connector import MojaloopConnector, create_mojaloop_connector
        
        mojaloop_config = {
            "endpoint": "https://test.mojaloop.io",
            "participant_id": "test-participant",
            "api_key": "test-api-key",
            "dry_run": True
        }
        
        mojaloop_connector = MojaloopConnector(mojaloop_config)
        print_success("Mojaloop connector created")
        
        # Test ISO 20022 connector
        from app.connectors.iso20022_connector import ISO20022Connector, create_iso20022_connector
        
        iso_config = {
            "bic": "TESTUS33XXX",
            "dry_run": True
        }
        
        iso_connector = ISO20022Connector(iso_config)
        print_success("ISO 20022 connector created")
        
        print_success("All connectors created successfully")
        return True
        
    except Exception as e:
        print_error(f"Connector test failed: {e}")
        return False

async def test_async_connectors():
    """Test async connector functionality"""
    print_header("Testing Async Connectors")
    
    try:
        # Test SWIFT connector async operations
        from app.connectors.swift_connector import create_swift_connector
        
        async with await create_swift_connector() as swift:
            print_success("SWIFT connector connected")
            
            # Test message creation
            class MockTransfer:
                def __init__(self):
                    self.transfer_id = "TRF123456"
                    self.amount = 1000.00
                    self.currency = "USD"
                    self.beneficiary_name = "John Doe"
                    self.beneficiary_iban = "US123456789"
                    self.beneficiary_bic = "BENEBICXXXXX"
                    self.created_at = datetime.now()
                    
                    class SourceAccount:
                        def __init__(self):
                            self.holder_name = "Jane Smith"
                            self.iban = "US987654321"
                    
                    self.source_account = SourceAccount()
            
            transfer = MockTransfer()
            message = swift.create_mt103_message(transfer)
            print_success(f"MT103 message created: {message.message_id}")
            
            result = await swift.send_message(message)
            print_success(f"SWIFT message sent: {result['status']}")
        
        # Test Mojaloop connector async operations
        from app.connectors.mojaloop_connector import create_mojaloop_connector
        
        async with await create_mojaloop_connector() as mojaloop:
            print_success("Mojaloop connector connected")
            
            quote = await mojaloop.create_quote(transfer)
            print_success(f"Mojaloop quote created: {quote['quoteId']}")
            
            transfer_result = await mojaloop.initiate_transfer(transfer, quote['quoteId'])
            print_success(f"Mojaloop transfer initiated: {transfer_result['transferId']}")
        
        print_success("All async connector tests passed")
        return True
        
    except Exception as e:
        print_error(f"Async connector test failed: {e}")
        return False

def test_models():
    """Test SQLAlchemy models"""
    print_header("Testing SQLAlchemy Models")
    
    try:
        from app.auth.models import User, UserRole
        from app.accounts.models import Account, AccountType, Currency
        from app.transfers.models import Transfer, TransferType, TransferStatus
        from app.kyc.models import KYCDocument, DocumentType, KYCStatus
        from app.audit.models import AuditLog, AuditSeverity
        
        # Test User model
        user = User(
            id="test-user-123",
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        print_success("User model created")
        
        # Test Account model
        account = Account(
            id="test-account-123",
            user_id="test-user-123",
            account_number="1234567890",
            iban="US123456789",
            account_type=AccountType.CHECKING,
            currency=Currency.USD,
            balance=10000.00
        )
        print_success("Account model created")
        
        # Test Transfer model
        transfer = Transfer(
            id="test-transfer-123",
            transfer_id="TRF123456",
            user_id="test-user-123",
            source_account_id="test-account-123",
            amount=1000.00,
            currency=Currency.USD,
            transfer_type=TransferType.SWIFT,
            status=TransferStatus.PENDING
        )
        print_success("Transfer model created")
        
        # Test KYC model
        kyc_doc = KYCDocument(
            id="test-kyc-123",
            user_id="test-user-123",
            document_type=DocumentType.PASSPORT,
            file_path="/uploads/passport.pdf",
            file_name="passport.pdf",
            file_size=1024000,
            mime_type="application/pdf",
            status=KYCStatus.PENDING
        )
        print_success("KYC document model created")
        
        # Test Audit model
        audit_log = AuditLog(
            id="test-audit-123",
            trace_id="trace-123",
            user_id="test-user-123",
            action="transfer_created",
            resource="/transfers",
            status="success"
        )
        print_success("Audit log model created")
        
        print_success("All models created successfully")
        return True
        
    except Exception as e:
        print_error(f"Model test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print_header("Testing Configuration")
    
    try:
        from app.config import get_settings
        
        settings = get_settings()
        print_success("Settings loaded")
        
        # Test database settings
        print_info(f"Database URL: {settings.database.url}")
        print_info(f"Database pool size: {settings.database.pool_size}")
        
        # Test security settings
        print_info(f"Secret key length: {len(settings.security.secret_key)}")
        print_info(f"Algorithm: {settings.security.algorithm}")
        
        # Test SWIFT settings
        print_info(f"SWIFT BIC: {settings.swift.bic}")
        print_info(f"SWIFT dry run: {settings.swift.dry_run}")
        
        # Test Mojaloop settings
        print_info(f"Mojaloop endpoint: {settings.mojaloop.endpoint}")
        print_info(f"Mojaloop dry run: {settings.mojaloop.dry_run}")
        
        print_success("Configuration test passed")
        return True
        
    except Exception as e:
        print_error(f"Configuration test failed: {e}")
        return False

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
        
        # Check volumes
        if "volumes" in compose_config:
            print_success("Volumes defined")
        else:
            print_warning("No volumes defined")
        
        # Check networks
        if "networks" in compose_config:
            print_success("Networks defined")
        else:
            print_warning("No networks defined")
        
        print_success("Docker Compose configuration valid")
        return True
        
    except Exception as e:
        print_error(f"Docker Compose test failed: {e}")
        return False

def test_makefile():
    """Test Makefile commands"""
    print_header("Testing Makefile")
    
    try:
        with open("Makefile", "r") as f:
            makefile_content = f.read()
        
        # Check for required targets
        required_targets = ["help", "build", "up", "down", "test", "migrate"]
        for target in required_targets:
            if f"{target}:" in makefile_content:
                print_success(f"Target {target} found")
            else:
                print_warning(f"Target {target} missing")
        
        print_success("Makefile test passed")
        return True
        
    except Exception as e:
        print_error(f"Makefile test failed: {e}")
        return False

async def main():
    """Main test function"""
    print_header("Banking Transfer Platform - Comprehensive Test")
    print_info(f"Test started at: {datetime.now()}")
    
    test_results = []
    
    # Run all tests
    tests = [
        ("File Structure", test_file_structure),
        ("Python Imports", test_python_imports),
        ("Connectors", test_connectors),
        ("Async Connectors", test_async_connectors),
        ("SQLAlchemy Models", test_models),
        ("Configuration", test_configuration),
        ("Docker Compose", test_docker_compose),
        ("Makefile", test_makefile),
    ]
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print_error(f"Test {test_name} failed with exception: {e}")
            test_results.append((test_name, False))
    
    # Print summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("All tests passed! Platform is ready for use.")
        return True
    else:
        print_warning(f"{total - passed} tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_info("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Test failed with unexpected error: {e}")
        sys.exit(1)