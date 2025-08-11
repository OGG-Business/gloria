-- Migration initiale pour la plateforme de transferts bancaires
-- Création des tables principales

-- Table des utilisateurs
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    nationality VARCHAR(2),
    id_number VARCHAR(50),
    id_type VARCHAR(20),
    kyc_status VARCHAR(20) DEFAULT 'NOT_VERIFIED',
    aml_status VARCHAR(20) DEFAULT 'NOT_CHECKED',
    risk_score INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100)
);

-- Table des comptes bancaires
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_number VARCHAR(50) UNIQUE NOT NULL,
    iban VARCHAR(34) UNIQUE,
    bic VARCHAR(11),
    account_name VARCHAR(100) NOT NULL,
    account_type VARCHAR(20) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    balance DECIMAL(19,4) NOT NULL DEFAULT 0,
    available_balance DECIMAL(19,4) NOT NULL DEFAULT 0,
    credit_limit DECIMAL(19,4),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    country_code VARCHAR(2) NOT NULL,
    bank_code VARCHAR(20),
    branch_code VARCHAR(20),
    owner_id UUID NOT NULL,
    owner_name VARCHAR(100) NOT NULL,
    owner_type VARCHAR(20) NOT NULL,
    kyc_status VARCHAR(20),
    aml_status VARCHAR(20),
    risk_score INTEGER DEFAULT 0,
    daily_limit DECIMAL(19,4),
    monthly_limit DECIMAL(19,4),
    opening_date TIMESTAMP,
    last_activity_date TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    CONSTRAINT fk_accounts_owner FOREIGN KEY (owner_id) REFERENCES users(id)
);

-- Table des transferts
CREATE TABLE transfers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reference VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'INITIATED',
    type VARCHAR(20) NOT NULL,
    sender_account_id UUID NOT NULL,
    beneficiary_account_id UUID NOT NULL,
    amount DECIMAL(19,4) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    exchange_rate DECIMAL(19,6),
    fees DECIMAL(19,4),
    total_amount DECIMAL(19,4),
    description VARCHAR(140),
    purpose_code VARCHAR(4),
    priority VARCHAR(4) DEFAULT 'NORMAL',
    execution_date TIMESTAMP,
    value_date TIMESTAMP,
    swift_message_id VARCHAR(100),
    iso_message_id VARCHAR(100),
    connector_type VARCHAR(20),
    connector_reference VARCHAR(100),
    error_code VARCHAR(10),
    error_message VARCHAR(500),
    kyc_status VARCHAR(20),
    aml_status VARCHAR(20),
    risk_score INTEGER DEFAULT 0,
    dry_run BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    CONSTRAINT fk_transfers_sender FOREIGN KEY (sender_account_id) REFERENCES accounts(id),
    CONSTRAINT fk_transfers_beneficiary FOREIGN KEY (beneficiary_account_id) REFERENCES accounts(id)
);

-- Table des événements de transfert
CREATE TABLE transfer_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transfer_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_code VARCHAR(20),
    description VARCHAR(500),
    details TEXT,
    error_code VARCHAR(20),
    error_message VARCHAR(500),
    source_system VARCHAR(50),
    external_reference VARCHAR(100),
    user_id VARCHAR(100),
    user_name VARCHAR(100),
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    session_id VARCHAR(100),
    trace_id VARCHAR(100),
    correlation_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_transfer_events_transfer FOREIGN KEY (transfer_id) REFERENCES transfers(id)
);

-- Table des logs d'audit
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    user_id VARCHAR(100),
    user_name VARCHAR(100),
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    session_id VARCHAR(100),
    trace_id VARCHAR(100),
    correlation_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des configurations système
CREATE TABLE system_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    config_type VARCHAR(20) DEFAULT 'STRING',
    description VARCHAR(500),
    is_encrypted BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100)
);

-- Table des connecteurs
CREATE TABLE connectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL,
    config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100)
);

-- Table des notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    data JSONB,
    is_read BOOLEAN DEFAULT false,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    CONSTRAINT fk_notifications_user FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Index pour optimiser les performances
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_kyc_status ON users(kyc_status);
CREATE INDEX idx_users_aml_status ON users(aml_status);

CREATE INDEX idx_accounts_iban ON accounts(iban);
CREATE INDEX idx_accounts_bic ON accounts(bic);
CREATE INDEX idx_accounts_owner ON accounts(owner_id);
CREATE INDEX idx_accounts_status ON accounts(status);
CREATE INDEX idx_accounts_country ON accounts(country_code);

CREATE INDEX idx_transfers_reference ON transfers(reference);
CREATE INDEX idx_transfers_status ON transfers(status);
CREATE INDEX idx_transfers_created_at ON transfers(created_at);
CREATE INDEX idx_transfers_sender_account ON transfers(sender_account_id);
CREATE INDEX idx_transfers_beneficiary_account ON transfers(beneficiary_account_id);
CREATE INDEX idx_transfers_type ON transfers(type);
CREATE INDEX idx_transfers_currency ON transfers(currency);

CREATE INDEX idx_transfer_events_transfer_id ON transfer_events(transfer_id);
CREATE INDEX idx_transfer_events_type ON transfer_events(event_type);
CREATE INDEX idx_transfer_events_created_at ON transfer_events(created_at);
CREATE INDEX idx_transfer_events_trace_id ON transfer_events(trace_id);

CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);

CREATE INDEX idx_system_configs_key ON system_configs(config_key);
CREATE INDEX idx_system_configs_active ON system_configs(is_active);

CREATE INDEX idx_connectors_type ON connectors(type);
CREATE INDEX idx_connectors_active ON connectors(is_active);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_read ON notifications(is_read);
CREATE INDEX idx_notifications_sent_at ON notifications(sent_at);

-- Triggers pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_accounts_updated_at BEFORE UPDATE ON accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transfers_updated_at BEFORE UPDATE ON transfers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_configs_updated_at BEFORE UPDATE ON system_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_connectors_updated_at BEFORE UPDATE ON connectors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Données initiales
INSERT INTO system_configs (config_key, config_value, config_type, description) VALUES
('SWIFT_ENABLED', 'false', 'BOOLEAN', 'Activer les transferts SWIFT'),
('MOJALOOP_ENABLED', 'false', 'BOOLEAN', 'Activer les transferts Mojaloop'),
('MAX_TRANSFER_AMOUNT', '1000000', 'DECIMAL', 'Montant maximum par transfert'),
('DAILY_TRANSFER_LIMIT', '10000000', 'DECIMAL', 'Limite quotidienne de transferts'),
('KYC_REQUIRED_AMOUNT', '10000', 'DECIMAL', 'Montant à partir duquel le KYC est obligatoire'),
('AML_SCREENING_ENABLED', 'true', 'BOOLEAN', 'Activer le screening AML'),
('AUDIT_LOG_RETENTION_DAYS', '2555', 'INTEGER', 'Durée de rétention des logs d''audit (7 ans)'),
('ENCRYPTION_ENABLED', 'true', 'BOOLEAN', 'Activer le chiffrement des données sensibles'),
('MFA_REQUIRED', 'true', 'BOOLEAN', 'Authentification multi-facteurs obligatoire'),
('SESSION_TIMEOUT_MINUTES', '30', 'INTEGER', 'Délai d''expiration de session');

-- Insertion d'un utilisateur admin par défaut
INSERT INTO users (username, email, first_name, last_name, kyc_status, aml_status, created_by) VALUES
('admin', 'admin@banking-transfer.com', 'Admin', 'User', 'VERIFIED', 'PASSED', 'system');

-- Insertion de comptes de test
INSERT INTO accounts (account_number, account_name, account_type, currency, balance, available_balance, country_code, owner_id, owner_name, owner_type, created_by) VALUES
('TEST001', 'Compte Test 1', 'CURRENT', 'USD', 100000.00, 100000.00, 'US', (SELECT id FROM users WHERE username = 'admin'), 'Admin User', 'INDIVIDUAL', 'system'),
('TEST002', 'Compte Test 2', 'CURRENT', 'EUR', 50000.00, 50000.00, 'FR', (SELECT id FROM users WHERE username = 'admin'), 'Admin User', 'INDIVIDUAL', 'system');