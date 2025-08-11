-- SwiftPay Audit and Monitoring Tables
-- Migration V3: Advanced audit, system monitoring, and compliance

-- System events table (for system-level audit)
CREATE TABLE system_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL,
    event_category VARCHAR(30) NOT NULL CHECK (event_category IN ('SECURITY', 'SYSTEM', 'BUSINESS', 'INTEGRATION')),
    severity VARCHAR(20) DEFAULT 'INFO' CHECK (severity IN ('DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')),
    source_service VARCHAR(50) NOT NULL,
    event_data JSONB,
    correlation_id UUID,
    session_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for system events
CREATE INDEX idx_system_events_type ON system_events(event_type);
CREATE INDEX idx_system_events_category ON system_events(event_category);
CREATE INDEX idx_system_events_severity ON system_events(severity);
CREATE INDEX idx_system_events_created_at ON system_events(created_at);
CREATE INDEX idx_system_events_correlation_id ON system_events(correlation_id) WHERE correlation_id IS NOT NULL;

-- Security events table (failed logins, suspicious activities)
CREATE TABLE security_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    event_type VARCHAR(50) NOT NULL,
    ip_address INET NOT NULL,
    user_agent TEXT,
    location_country VARCHAR(3),
    location_city VARCHAR(100),
    risk_score DECIMAL(5,2), -- 0.00 to 100.00
    blocked BOOLEAN DEFAULT FALSE,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for security events
CREATE INDEX idx_security_events_user_id ON security_events(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_security_events_type ON security_events(event_type);
CREATE INDEX idx_security_events_ip ON security_events(ip_address);
CREATE INDEX idx_security_events_created_at ON security_events(created_at);
CREATE INDEX idx_security_events_risk_score ON security_events(risk_score) WHERE risk_score IS NOT NULL;

-- Rate limiting table
CREATE TABLE rate_limits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    identifier VARCHAR(255) NOT NULL, -- IP address, user ID, or API key
    identifier_type VARCHAR(20) NOT NULL CHECK (identifier_type IN ('IP', 'USER', 'API_KEY')),
    endpoint VARCHAR(255) NOT NULL,
    request_count INTEGER NOT NULL DEFAULT 1,
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    window_duration_minutes INTEGER NOT NULL DEFAULT 60,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(identifier, identifier_type, endpoint, window_start)
);

-- Index for rate limiting lookups
CREATE INDEX idx_rate_limits_lookup ON rate_limits(identifier, identifier_type, endpoint, window_start);
CREATE INDEX idx_rate_limits_cleanup ON rate_limits(window_start);

-- Message queue table (for async processing)
CREATE TABLE message_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    queue_name VARCHAR(100) NOT NULL,
    message_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'DEAD_LETTER')),
    max_retries INTEGER DEFAULT 3,
    retry_count INTEGER DEFAULT 0,
    scheduled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    correlation_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for message queue
CREATE INDEX idx_message_queue_status ON message_queue(status);
CREATE INDEX idx_message_queue_scheduled ON message_queue(scheduled_at) WHERE status = 'PENDING';
CREATE INDEX idx_message_queue_queue_name ON message_queue(queue_name);
CREATE INDEX idx_message_queue_correlation_id ON message_queue(correlation_id) WHERE correlation_id IS NOT NULL;

-- System health metrics
CREATE TABLE system_health_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    metric_unit VARCHAR(20),
    service_name VARCHAR(50) NOT NULL,
    instance_id VARCHAR(100),
    tags JSONB,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Partition system_health_metrics by month for performance
CREATE INDEX idx_system_health_metrics_recorded_at ON system_health_metrics(recorded_at);
CREATE INDEX idx_system_health_metrics_service ON system_health_metrics(service_name, metric_name);

-- Compliance reports table
CREATE TABLE compliance_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_type VARCHAR(50) NOT NULL,
    report_period_start DATE NOT NULL,
    report_period_end DATE NOT NULL,
    generated_by UUID NOT NULL REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'GENERATING' CHECK (status IN ('GENERATING', 'COMPLETED', 'FAILED')),
    file_path VARCHAR(500),
    file_size BIGINT,
    encryption_key_id VARCHAR(100),
    report_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Transaction limits per user
CREATE TABLE user_transaction_limits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    currency VARCHAR(3) NOT NULL,
    daily_limit DECIMAL(15,2) NOT NULL,
    monthly_limit DECIMAL(15,2) NOT NULL,
    single_transaction_limit DECIMAL(15,2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    effective_date DATE NOT NULL,
    expires_date DATE,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, currency, effective_date)
);

-- Daily transaction aggregates (for limit checking)
CREATE TABLE daily_transaction_aggregates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_date DATE NOT NULL,
    currency VARCHAR(3) NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    transaction_count INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, transaction_date, currency)
);

-- Monthly transaction aggregates
CREATE TABLE monthly_transaction_aggregates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    currency VARCHAR(3) NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    transaction_count INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, year, month, currency)
);

-- Suspicious activity reports (SAR)
CREATE TABLE suspicious_activity_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sar_number VARCHAR(50) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    transfer_ids UUID[] NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    suspicion_reason TEXT NOT NULL,
    description TEXT NOT NULL,
    amount_involved DECIMAL(15,2),
    currency VARCHAR(3),
    filing_required BOOLEAN DEFAULT TRUE,
    filed_with_authority BOOLEAN DEFAULT FALSE,
    filing_date DATE,
    filing_reference VARCHAR(100),
    status VARCHAR(20) DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'PENDING_REVIEW', 'FILED', 'CLOSED')),
    created_by UUID NOT NULL REFERENCES users(id),
    reviewed_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- SWIFT message log (for debugging and compliance)
CREATE TABLE swift_message_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transfer_id UUID REFERENCES transfers(id),
    message_type VARCHAR(10) NOT NULL, -- MT103, pacs.008, etc.
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('OUTBOUND', 'INBOUND')),
    swift_message_id VARCHAR(100),
    raw_message TEXT NOT NULL,
    parsed_message JSONB,
    validation_status VARCHAR(20) DEFAULT 'PENDING' CHECK (validation_status IN ('PENDING', 'VALID', 'INVALID')),
    validation_errors TEXT[],
    sent_at TIMESTAMP WITH TIME ZONE,
    received_at TIMESTAMP WITH TIME ZONE,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    correlation_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for SWIFT message log
CREATE INDEX idx_swift_message_log_transfer_id ON swift_message_log(transfer_id) WHERE transfer_id IS NOT NULL;
CREATE INDEX idx_swift_message_log_message_id ON swift_message_log(swift_message_id) WHERE swift_message_id IS NOT NULL;
CREATE INDEX idx_swift_message_log_direction ON swift_message_log(direction);
CREATE INDEX idx_swift_message_log_created_at ON swift_message_log(created_at);

-- Apply updated_at triggers to new tables
CREATE TRIGGER update_user_kyc_updated_at BEFORE UPDATE ON user_kyc
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_transaction_limits_updated_at BEFORE UPDATE ON user_transaction_limits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_suspicious_activity_reports_updated_at BEFORE UPDATE ON suspicious_activity_reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_country_risk_ratings_updated_at BEFORE UPDATE ON country_risk_ratings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create materialized view for compliance dashboard
CREATE MATERIALIZED VIEW compliance_dashboard AS
SELECT 
    DATE(t.created_at) as transaction_date,
    t.currency,
    cr.country_name as destination_country,
    cr.risk_level,
    COUNT(*) as transaction_count,
    SUM(t.amount) as total_amount,
    COUNT(CASE WHEN ss.status = 'HIT' THEN 1 END) as sanctions_hits,
    COUNT(CASE WHEN aa.severity IN ('HIGH', 'CRITICAL') THEN 1 END) as high_risk_alerts
FROM transfers t
LEFT JOIN country_risk_ratings cr ON t.recipient_country_code = cr.country_code
LEFT JOIN sanctions_screening ss ON t.id = ss.transfer_id
LEFT JOIN aml_alerts aa ON t.id = aa.transfer_id
GROUP BY DATE(t.created_at), t.currency, cr.country_name, cr.risk_level
ORDER BY transaction_date DESC;

-- Create unique index for materialized view refresh
CREATE UNIQUE INDEX idx_compliance_dashboard_unique ON compliance_dashboard(transaction_date, currency, COALESCE(destination_country, 'UNKNOWN'), COALESCE(risk_level, 'UNKNOWN'));

-- Function to refresh compliance dashboard
CREATE OR REPLACE FUNCTION refresh_compliance_dashboard()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY compliance_dashboard;
END;
$$ LANGUAGE plpgsql;

-- Create a function to clean up old data
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS VOID AS $$
BEGIN
    -- Clean up old rate limit records (older than 24 hours)
    DELETE FROM rate_limits WHERE window_start < CURRENT_TIMESTAMP - INTERVAL '24 hours';
    
    -- Clean up old system health metrics (older than 30 days)
    DELETE FROM system_health_metrics WHERE recorded_at < CURRENT_TIMESTAMP - INTERVAL '30 days';
    
    -- Clean up completed message queue items (older than 7 days)
    DELETE FROM message_queue WHERE status = 'COMPLETED' AND completed_at < CURRENT_TIMESTAMP - INTERVAL '7 days';
    
    -- Archive old audit logs (move to separate table or external storage)
    -- This is a placeholder - implement based on retention policy
    
END;
$$ LANGUAGE plpgsql;