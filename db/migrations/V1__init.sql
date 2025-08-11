-- Flyway migration: initial schema
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(64) UNIQUE,
    owner_name TEXT NOT NULL,
    iban VARCHAR(34) NOT NULL,
    bic VARCHAR(11) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS transfers (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(64) UNIQUE,
    amount NUMERIC(18,2) NOT NULL,
    currency CHAR(3) NOT NULL,
    debtor_iban VARCHAR(34) NOT NULL,
    debtor_bic VARCHAR(11) NOT NULL,
    creditor_iban VARCHAR(34) NOT NULL,
    creditor_bic VARCHAR(11) NOT NULL,
    remittance_info TEXT,
    state VARCHAR(16) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS transfer_events (
    id SERIAL PRIMARY KEY,
    transfer_id INTEGER REFERENCES transfers(id) ON DELETE CASCADE,
    event_type VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    action VARCHAR(64) NOT NULL,
    subject VARCHAR(128) NOT NULL,
    actor VARCHAR(128) NOT NULL,
    details JSONB NOT NULL,
    prev_hash VARCHAR(128),
    hash VARCHAR(128) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);