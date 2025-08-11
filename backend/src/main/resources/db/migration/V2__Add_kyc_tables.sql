-- SwiftPay KYC/AML Tables
-- Migration V2: KYC verification and compliance

-- KYC verification levels
CREATE TABLE kyc_levels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    level_name VARCHAR(50) UNIQUE NOT NULL,
    max_daily_amount DECIMAL(15,2) NOT NULL,
    max_monthly_amount DECIMAL(15,2) NOT NULL,
    required_documents TEXT[] NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert default KYC levels
INSERT INTO kyc_levels (level_name, max_daily_amount, max_monthly_amount, required_documents, description) VALUES
('BASIC', 500.00, 2000.00, '["government_id"]', 'Basic verification with government ID'),
('STANDARD', 5000.00, 20000.00, '["government_id", "proof_of_address"]', 'Standard verification with ID and address proof'),
('PREMIUM', 50000.00, 200000.00, '["government_id", "proof_of_address", "proof_of_income"]', 'Premium verification with full documentation'),
('BUSINESS', 500000.00, 2000000.00, '["business_registration", "beneficial_ownership", "bank_statements"]', 'Business account verification');

-- User KYC status
CREATE TABLE user_kyc (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    kyc_level_id UUID NOT NULL REFERENCES kyc_levels(id),
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'IN_REVIEW', 'APPROVED', 'REJECTED', 'EXPIRED')),
    submitted_at TIMESTAMP WITH TIME ZONE,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    approved_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    reviewer_id UUID REFERENCES users(id),
    rejection_reason TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, kyc_level_id)
);

-- KYC documents
CREATE TABLE kyc_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_kyc_id UUID NOT NULL REFERENCES user_kyc(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL, -- Encrypted file path
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    document_hash VARCHAR(255) NOT NULL, -- SHA-256 hash for integrity
    encryption_key_id VARCHAR(100) NOT NULL, -- Reference to Vault key
    status VARCHAR(20) DEFAULT 'UPLOADED' CHECK (status IN ('UPLOADED', 'VERIFIED', 'REJECTED')),
    verification_notes TEXT,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP WITH TIME ZONE,
    verified_by UUID REFERENCES users(id)
);

-- Sanctions screening table
CREATE TABLE sanctions_screening (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    transfer_id UUID REFERENCES transfers(id),
    screening_type VARCHAR(20) CHECK (screening_type IN ('USER', 'TRANSFER', 'COUNTERPARTY')),
    entity_name VARCHAR(255) NOT NULL,
    screening_provider VARCHAR(50) NOT NULL,
    screening_reference VARCHAR(100),
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'CLEAR', 'HIT', 'FALSE_POSITIVE', 'ERROR')),
    risk_score DECIMAL(5,2), -- 0.00 to 100.00
    matches JSONB, -- Detailed match information
    screened_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    reviewed_by UUID REFERENCES users(id),
    review_notes TEXT,
    
    -- At least one of user_id or transfer_id must be set
    CONSTRAINT check_screening_entity CHECK (user_id IS NOT NULL OR transfer_id IS NOT NULL)
);

-- AML transaction monitoring
CREATE TABLE aml_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    transfer_id UUID REFERENCES transfers(id),
    alert_type VARCHAR(50) NOT NULL,
    alert_rule VARCHAR(100) NOT NULL,
    severity VARCHAR(20) DEFAULT 'MEDIUM' CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    description TEXT NOT NULL,
    alert_data JSONB,
    status VARCHAR(20) DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'INVESTIGATING', 'RESOLVED', 'FALSE_POSITIVE')),
    assigned_to UUID REFERENCES users(id),
    resolution_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Country risk ratings
CREATE TABLE country_risk_ratings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    country_code VARCHAR(3) UNIQUE NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    risk_level VARCHAR(20) DEFAULT 'MEDIUM' CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'PROHIBITED')),
    fatf_rating VARCHAR(10), -- FATF compliance rating
    transparency_score DECIMAL(5,2), -- Transparency International score
    additional_due_diligence BOOLEAN DEFAULT FALSE,
    enhanced_monitoring BOOLEAN DEFAULT FALSE,
    notes TEXT,
    effective_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert default country risk ratings (focus on DRC and African countries)
INSERT INTO country_risk_ratings (country_code, country_name, risk_level, additional_due_diligence, enhanced_monitoring, effective_date) VALUES
('COD', 'Democratic Republic of Congo', 'HIGH', TRUE, TRUE, CURRENT_DATE),
('CMR', 'Cameroon', 'MEDIUM', TRUE, FALSE, CURRENT_DATE),
('SEN', 'Senegal', 'MEDIUM', FALSE, FALSE, CURRENT_DATE),
('CIV', 'Côte d''Ivoire', 'MEDIUM', FALSE, FALSE, CURRENT_DATE),
('BFA', 'Burkina Faso', 'HIGH', TRUE, TRUE, CURRENT_DATE),
('MLI', 'Mali', 'HIGH', TRUE, TRUE, CURRENT_DATE),
('USA', 'United States', 'LOW', FALSE, FALSE, CURRENT_DATE),
('GBR', 'United Kingdom', 'LOW', FALSE, FALSE, CURRENT_DATE),
('DEU', 'Germany', 'LOW', FALSE, FALSE, CURRENT_DATE),
('FRA', 'France', 'LOW', FALSE, FALSE, CURRENT_DATE);

-- Indexes for KYC/AML tables
CREATE INDEX idx_user_kyc_user_id ON user_kyc(user_id);
CREATE INDEX idx_user_kyc_status ON user_kyc(status);
CREATE INDEX idx_kyc_documents_user_kyc_id ON kyc_documents(user_kyc_id);
CREATE INDEX idx_sanctions_screening_user_id ON sanctions_screening(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_sanctions_screening_transfer_id ON sanctions_screening(transfer_id) WHERE transfer_id IS NOT NULL;
CREATE INDEX idx_aml_alerts_user_id ON aml_alerts(user_id);
CREATE INDEX idx_aml_alerts_status ON aml_alerts(status);
CREATE INDEX idx_country_risk_country_code ON country_risk_ratings(country_code);

-- Apply updated_at triggers
CREATE TRIGGER update_user_kyc_updated_at BEFORE UPDATE ON user_kyc
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_country_risk_ratings_updated_at BEFORE UPDATE ON country_risk_ratings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();