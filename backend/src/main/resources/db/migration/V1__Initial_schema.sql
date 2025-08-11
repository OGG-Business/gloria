-- SwiftPay Initial Database Schema
-- Migration V1: Core tables for banking transfers

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    nationality VARCHAR(3), -- ISO 3166-1 alpha-3
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'SUSPENDED', 'BLOCKED', 'PENDING_VERIFICATION')),
    role VARCHAR(20) DEFAULT 'USER' CHECK (role IN ('USER', 'OPERATOR', 'ADMIN')),
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bank accounts table
CREATE TABLE bank_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_name VARCHAR(255) NOT NULL,
    iban VARCHAR(34), -- IBAN can be up to 34 characters
    bic VARCHAR(11), -- BIC/SWIFT code
    account_number VARCHAR(50), -- For non-IBAN countries
    bank_name VARCHAR(255) NOT NULL,
    bank_address TEXT,
    country_code VARCHAR(3) NOT NULL, -- ISO 3166-1 alpha-3
    currency VARCHAR(3) NOT NULL, -- ISO 4217
    account_type VARCHAR(20) DEFAULT 'CHECKING' CHECK (account_type IN ('CHECKING', 'SAVINGS', 'BUSINESS')),
    is_verified BOOLEAN DEFAULT FALSE,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure IBAN or account_number is provided
    CONSTRAINT check_account_identifier CHECK (iban IS NOT NULL OR account_number IS NOT NULL)
);

-- Create index for performance
CREATE INDEX idx_bank_accounts_user_id ON bank_accounts(user_id);
CREATE INDEX idx_bank_accounts_iban ON bank_accounts(iban) WHERE iban IS NOT NULL;

-- Transfers table
CREATE TABLE transfers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reference_number VARCHAR(50) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    from_account_id UUID NOT NULL REFERENCES bank_accounts(id),
    to_account_id UUID, -- Can be NULL for external transfers
    
    -- Recipient details (for external transfers)
    recipient_name VARCHAR(255),
    recipient_iban VARCHAR(34),
    recipient_bic VARCHAR(11),
    recipient_account_number VARCHAR(50),
    recipient_bank_name VARCHAR(255),
    recipient_bank_address TEXT,
    recipient_country_code VARCHAR(3),
    
    -- Transfer details
    amount DECIMAL(15,2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) NOT NULL,
    exchange_rate DECIMAL(10,6),
    fee_amount DECIMAL(15,2) DEFAULT 0,
    total_amount DECIMAL(15,2) NOT NULL,
    
    -- Transfer metadata
    purpose_code VARCHAR(10), -- ISO 20022 purpose codes
    remittance_info TEXT,
    urgent BOOLEAN DEFAULT FALSE,
    
    -- Status and timing
    status VARCHAR(20) DEFAULT 'INITIATED' CHECK (status IN ('INITIATED', 'PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED')),
    initiated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    expected_completion_date DATE,
    
    -- External system references
    swift_message_id VARCHAR(100),
    mojaloop_transaction_id VARCHAR(100),
    bank_reference VARCHAR(100),
    
    -- Error handling
    error_code VARCHAR(50),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for transfers
CREATE INDEX idx_transfers_user_id ON transfers(user_id);
CREATE INDEX idx_transfers_status ON transfers(status);
CREATE INDEX idx_transfers_reference ON transfers(reference_number);
CREATE INDEX idx_transfers_created_at ON transfers(created_at);
CREATE INDEX idx_transfers_swift_message_id ON transfers(swift_message_id) WHERE swift_message_id IS NOT NULL;

-- Transfer events table (for audit trail and state machine)
CREATE TABLE transfer_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transfer_id UUID NOT NULL REFERENCES transfers(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    from_status VARCHAR(20),
    to_status VARCHAR(20),
    event_data JSONB,
    correlation_id UUID, -- For tracing
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure chronological order
    CONSTRAINT check_event_order CHECK (created_at >= (
        SELECT COALESCE(MAX(created_at), '1970-01-01'::timestamp with time zone)
        FROM transfer_events te2 
        WHERE te2.transfer_id = transfer_events.transfer_id 
        AND te2.id != transfer_events.id
    ))
);

-- Indexes for transfer events
CREATE INDEX idx_transfer_events_transfer_id ON transfer_events(transfer_id);
CREATE INDEX idx_transfer_events_created_at ON transfer_events(created_at);
CREATE INDEX idx_transfer_events_correlation_id ON transfer_events(correlation_id) WHERE correlation_id IS NOT NULL;

-- Exchange rates table
CREATE TABLE exchange_rates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_currency VARCHAR(3) NOT NULL,
    to_currency VARCHAR(3) NOT NULL,
    rate DECIMAL(10,6) NOT NULL,
    effective_date DATE NOT NULL,
    source VARCHAR(50) NOT NULL, -- ECB, Fed, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(from_currency, to_currency, effective_date)
);

-- Fees configuration table
CREATE TABLE fee_configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    from_country VARCHAR(3),
    to_country VARCHAR(3),
    currency VARCHAR(3),
    min_amount DECIMAL(15,2),
    max_amount DECIMAL(15,2),
    fee_type VARCHAR(20) CHECK (fee_type IN ('FIXED', 'PERCENTAGE', 'TIERED')),
    fee_value DECIMAL(10,4) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit log table (append-only)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    user_id UUID REFERENCES users(id),
    ip_address INET,
    user_agent TEXT,
    correlation_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for audit logs
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_correlation_id ON audit_logs(correlation_id) WHERE correlation_id IS NOT NULL;

-- API keys table for external integrations
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    permissions JSONB NOT NULL DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Webhook endpoints table
CREATE TABLE webhook_endpoints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url VARCHAR(500) NOT NULL,
    secret VARCHAR(255) NOT NULL,
    events TEXT[] NOT NULL, -- Array of event types to subscribe to
    is_active BOOLEAN DEFAULT TRUE,
    retry_count INTEGER DEFAULT 3,
    timeout_seconds INTEGER DEFAULT 30,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Webhook delivery attempts table
CREATE TABLE webhook_deliveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    webhook_endpoint_id UUID NOT NULL REFERENCES webhook_endpoints(id) ON DELETE CASCADE,
    transfer_id UUID REFERENCES transfers(id),
    event_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    http_status INTEGER,
    response_body TEXT,
    attempt_number INTEGER NOT NULL DEFAULT 1,
    delivered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System configuration table
CREATE TABLE system_configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE,
    updated_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert default system configurations
INSERT INTO system_configurations (config_key, config_value, description) VALUES
('max_daily_transfer_amount', '50000.00', 'Maximum daily transfer amount in USD'),
('max_single_transfer_amount', '10000.00', 'Maximum single transfer amount in USD'),
('kyc_required_amount', '1000.00', 'Minimum amount requiring KYC verification'),
('transfer_timeout_hours', '72', 'Transfer timeout in hours'),
('supported_currencies', '["USD","EUR","GBP","JPY","CHF","CAD","AUD","CDF","XAF","XOF"]', 'List of supported currencies'),
('supported_countries', '["US","GB","DE","FR","IT","ES","CD","CM","SN","CI","BF","ML"]', 'List of supported countries'),
('maintenance_mode', 'false', 'System maintenance mode flag');

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bank_accounts_updated_at BEFORE UPDATE ON bank_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transfers_updated_at BEFORE UPDATE ON transfers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fee_configurations_updated_at BEFORE UPDATE ON fee_configurations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_webhook_endpoints_updated_at BEFORE UPDATE ON webhook_endpoints
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_configurations_updated_at BEFORE UPDATE ON system_configurations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for reporting
CREATE VIEW transfer_summary AS
SELECT 
    DATE(created_at) as transfer_date,
    status,
    currency,
    COUNT(*) as transfer_count,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount
FROM transfers
GROUP BY DATE(created_at), status, currency;

CREATE VIEW daily_metrics AS
SELECT 
    DATE(created_at) as metric_date,
    COUNT(*) as total_transfers,
    COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed_transfers,
    COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed_transfers,
    SUM(amount) as total_volume,
    AVG(amount) as avg_transfer_amount
FROM transfers
GROUP BY DATE(created_at)
ORDER BY metric_date DESC;