"""
Configuration pour les tests de connecteurs bancaires
"""
import pytest
from typing import Dict, Any


@pytest.fixture
def swift_test_config() -> Dict[str, Any]:
    """Configuration de test pour SWIFT"""
    return {
        "bic": "TESTBIC",
        "cert_path": "/test/cert.pem",
        "key_path": "/test/key.pem",
        "endpoint": "https://test.swift.com",
        "timeout": 30,
        "dry_run": True,
        "message_types": ["MT103", "MT910", "MT202", "MT210"],
        "priority_levels": ["normal", "urgent", "high"],
        "currencies": ["USD", "EUR", "GBP", "JPY", "CHF"],
        "test_messages": {
            "mt103": """
            {1:F01TESTBICXXXXAXXX1234567890}
            {2:O1031234567890TESTBICXXXXAXXX1234567890N}
            {3:{113:SEPA}{108:ILOVESEPA}}
            {4:
            :20:REF123456789
            :23B:CRED
            :32A:240101USD1000,00
            :50K:/12345678901234567890
            Test Sender
            :59:/98765432109876543210
            Test Receiver
            :70:Test transfer
            :71A:SHA
            -}
            {5:{CHK:1234567890ABC}{TNG:}}
            """,
            "mt910": """
            {1:F01CHASUS33XXXXAXXX1234567890}
            {2:O9101234567890CHASUS33XXXXAXXX1234567890N}
            {3:{113:SEPA}{108:ILOVESEPA}}
            {4:
            :20:REF123456789
            :25:12345678901234567890
            :32A:240101USD1000,00
            :61:2401010101D1000,00NTRFREF123456789
            :86:Test credit
            -}
            {5:{CHK:1234567890ABC}{TNG:}}
            """
        }
    }


@pytest.fixture
def mojaloop_test_config() -> Dict[str, Any]:
    """Configuration de test pour Mojaloop"""
    return {
        "endpoint": "https://test.mojaloop.com",
        "timeout": 30,
        "dry_run": True,
        "participant_id": "test-participant",
        "currency": "USD",
        "test_transfers": {
            "simple": {
                "transferId": "test-transfer-123",
                "payer": {
                    "partyIdInfo": {
                        "partyIdType": "MSISDN",
                        "partyIdentifier": "1234567890",
                        "fspId": "test-fsp"
                    }
                },
                "payee": {
                    "partyIdInfo": {
                        "partyIdType": "MSISDN",
                        "partyIdentifier": "0987654321",
                        "fspId": "test-fsp"
                    }
                },
                "amountType": "SEND",
                "currency": "USD",
                "amount": "100.00"
            },
            "complex": {
                "transferId": "test-transfer-456",
                "payer": {
                    "partyIdInfo": {
                        "partyIdType": "ACCOUNT_ID",
                        "partyIdentifier": "12345678901234567890",
                        "fspId": "test-fsp"
                    },
                    "personalInfo": {
                        "complexName": {
                            "firstName": "Test",
                            "lastName": "Sender"
                        },
                        "dateOfBirth": "1990-01-01"
                    }
                },
                "payee": {
                    "partyIdInfo": {
                        "partyIdType": "ACCOUNT_ID",
                        "partyIdentifier": "09876543210987654321",
                        "fspId": "test-fsp"
                    },
                    "personalInfo": {
                        "complexName": {
                            "firstName": "Test",
                            "lastName": "Receiver"
                        },
                        "dateOfBirth": "1990-01-01"
                    }
                },
                "amountType": "SEND",
                "currency": "USD",
                "amount": "500.00",
                "note": "Test transfer"
            }
        }
    }


@pytest.fixture
def iso20022_test_config() -> Dict[str, Any]:
    """Configuration de test pour ISO 20022"""
    return {
        "message_types": ["pacs.008", "pacs.002", "pacs.004", "camt.052", "camt.053"],
        "test_messages": {
            "pacs008": """
            <?xml version="1.0" encoding="UTF-8"?>
            <Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
                <FIToFICstmrCdtTrf>
                    <GrpHdr>
                        <MsgId>MSG123456789</MsgId>
                        <CreDtTm>2024-01-01T10:00:00</CreDtTm>
                        <NbOfTxs>1</NbOfTxs>
                        <TtlIntrBkSttlmAmt Ccy="USD">1000.00</TtlIntrBkSttlmAmt>
                        <IntrBkSttlmDt>2024-01-01</IntrBkSttlmDt>
                        <SttlmInf>
                            <SttlmMtd>CLRG</SttlmMtd>
                        </SttlmInf>
                    </GrpHdr>
                    <CdtTrfTxInf>
                        <PmtId>
                            <InstrId>INSTR123456</InstrId>
                            <EndToEndId>E2E123456789</EndToEndId>
                        </PmtId>
                        <IntrBkSttlmAmt Ccy="USD">1000.00</IntrBkSttlmAmt>
                        <IntrBkSttlmDt>2024-01-01</IntrBkSttlmDt>
                        <SttlmTmReq>
                            <DbtDtTm>2024-01-01T10:00:00</DbtDtTm>
                            <RjctDtTm>2024-01-01T10:00:00</RjctDtTm>
                        </SttlmTmReq>
                        <InstgAgt>
                            <FinInstnId>
                                <BICFI>TESTBIC</BICFI>
                            </FinInstnId>
                        </InstgAgt>
                        <InstdAgt>
                            <FinInstnId>
                                <BICFI>CHASUS33</BICFI>
                            </FinInstnId>
                        </InstdAgt>
                        <Dbtr>
                            <Nm>Test Sender</Nm>
                            <PstlAdr>
                                <Ctry>FR</Ctry>
                            </PstlAdr>
                        </Dbtr>
                        <DbtrAcct>
                            <Id>
                                <Othr>
                                    <Id>12345678901234567890</Id>
                                </Othr>
                            </Id>
                        </DbtrAcct>
                        <DbtrAgt>
                            <FinInstnId>
                                <BICFI>TESTBIC</BICFI>
                            </FinInstnId>
                        </DbtrAgt>
                        <CdtrAgt>
                            <FinInstnId>
                                <BICFI>CHASUS33</BICFI>
                            </FinInstnId>
                        </CdtrAgt>
                        <Cdtr>
                            <Nm>Test Receiver</Nm>
                            <PstlAdr>
                                <Ctry>US</Ctry>
                            </PstlAdr>
                        </Cdtr>
                        <CdtrAcct>
                            <Id>
                                <Othr>
                                    <Id>09876543210987654321</Id>
                                </Othr>
                            </Id>
                        </CdtrAcct>
                        <Purp>
                            <Cd>SUPP</Cd>
                        </Purp>
                        <RmtInf>
                            <Ustrd>Test transfer</Ustrd>
                        </RmtInf>
                    </CdtTrfTxInf>
                </FIToFICstmrCdtTrf>
            </Document>
            """,
            "pacs002": """
            <?xml version="1.0" encoding="UTF-8"?>
            <Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.002.001.10">
                <FIToFIPmtStsRpt>
                    <GrpHdr>
                        <MsgId>MSG123456789</MsgId>
                        <CreDtTm>2024-01-01T10:00:00</CreDtTm>
                        <NbOfTxs>1</NbOfTxs>
                    </GrpHdr>
                    <TxInfAndSts>
                        <OrgnlTxId>MSG123456789</OrgnlTxId>
                        <TxSts>ACSP</TxSts>
                        <StsRsnInf>
                            <Rsn>
                                <Cd>AC01</Cd>
                            </Rsn>
                        </StsRsnInf>
                    </TxInfAndSts>
                </FIToFIPmtStsRpt>
            </Document>
            """
        }
    }


@pytest.fixture
def bank_connectivity_test_config() -> Dict[str, Any]:
    """Configuration pour les tests de connectivité bancaire"""
    return {
        "test_endpoints": {
            "swift": {
                "url": "https://test.swift.com",
                "timeout": 30,
                "expected_status": 200,
                "expected_response": {"status": "ok"}
            },
            "mojaloop": {
                "url": "https://test.mojaloop.com",
                "timeout": 30,
                "expected_status": 200,
                "expected_response": {"status": "ok"}
            },
            "iso20022": {
                "url": "https://test.iso20022.com",
                "timeout": 30,
                "expected_status": 200,
                "expected_response": {"status": "ok"}
            }
        },
        "certificate_tests": {
            "valid_cert": {
                "path": "/test/valid.crt",
                "expected_result": True
            },
            "invalid_cert": {
                "path": "/test/invalid.crt",
                "expected_result": False
            },
            "expired_cert": {
                "path": "/test/expired.crt",
                "expected_result": False
            }
        },
        "network_tests": {
            "ping": {
                "host": "test.swift.com",
                "expected_result": True
            },
            "dns": {
                "host": "test.swift.com",
                "expected_result": True
            },
            "tls": {
                "host": "test.swift.com",
                "port": 443,
                "expected_result": True
            }
        }
    }


@pytest.fixture
def performance_test_config() -> Dict[str, Any]:
    """Configuration pour les tests de performance"""
    return {
        "load_test": {
            "concurrent_users": 100,
            "duration_seconds": 300,
            "ramp_up_seconds": 60,
            "target_rps": 50
        },
        "stress_test": {
            "concurrent_users": 500,
            "duration_seconds": 600,
            "ramp_up_seconds": 120,
            "target_rps": 100
        },
        "endurance_test": {
            "concurrent_users": 50,
            "duration_seconds": 3600,
            "ramp_up_seconds": 300,
            "target_rps": 25
        },
        "spike_test": {
            "concurrent_users": 1000,
            "duration_seconds": 60,
            "ramp_up_seconds": 10,
            "target_rps": 200
        }
    }


@pytest.fixture
def security_test_config() -> Dict[str, Any]:
    """Configuration pour les tests de sécurité"""
    return {
        "authentication_tests": {
            "valid_credentials": {
                "username": "testuser",
                "password": "testpass123",
                "expected_result": True
            },
            "invalid_credentials": {
                "username": "testuser",
                "password": "wrongpassword",
                "expected_result": False
            },
            "locked_account": {
                "username": "lockeduser",
                "password": "testpass123",
                "expected_result": False
            }
        },
        "authorization_tests": {
            "admin_access": {
                "user_role": "admin",
                "endpoint": "/admin/users",
                "expected_result": True
            },
            "user_access": {
                "user_role": "user",
                "endpoint": "/admin/users",
                "expected_result": False
            }
        },
        "input_validation_tests": {
            "sql_injection": {
                "input": "'; DROP TABLE users; --",
                "expected_result": False
            },
            "xss": {
                "input": "<script>alert('xss')</script>",
                "expected_result": False
            },
            "path_traversal": {
                "input": "../../../etc/passwd",
                "expected_result": False
            }
        },
        "encryption_tests": {
            "sensitive_data": [
                "password",
                "credit_card",
                "ssn",
                "iban"
            ],
            "encryption_required": True
        }
    }


@pytest.fixture
def compliance_test_config() -> Dict[str, Any]:
    """Configuration pour les tests de conformité"""
    return {
        "kyc_requirements": {
            "document_types": ["identity_card", "passport", "drivers_license"],
            "required_fields": ["full_name", "date_of_birth", "nationality", "address"],
            "verification_methods": ["document_scan", "biometric", "video_call"]
        },
        "aml_requirements": {
            "transfer_limits": {
                "daily": 10000,
                "monthly": 50000,
                "yearly": 500000
            },
            "screening_required": True,
            "sanctions_lists": ["UN", "EU", "US", "UK"],
            "pep_screening": True
        },
        "data_retention": {
            "transaction_records": "7_years",
            "kyc_documents": "5_years",
            "audit_logs": "10_years"
        },
        "privacy_requirements": {
            "gdpr_compliance": True,
            "data_encryption": True,
            "right_to_forget": True,
            "consent_management": True
        }
    }