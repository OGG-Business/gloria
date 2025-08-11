CREATE TABLE IF NOT EXISTS accounts (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR NOT NULL,
  name VARCHAR NOT NULL,
  iban VARCHAR NOT NULL,
  bic VARCHAR NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_accounts_iban ON accounts(iban);

CREATE TABLE IF NOT EXISTS transfers (
  id SERIAL PRIMARY KEY,
  debtor_account_id INTEGER NOT NULL REFERENCES accounts(id),
  creditor_name VARCHAR NOT NULL,
  creditor_iban VARCHAR NOT NULL,
  creditor_bic VARCHAR NULL,
  amount NUMERIC(18,2) NOT NULL,
  currency VARCHAR NOT NULL DEFAULT 'USD',
  status VARCHAR NOT NULL DEFAULT 'INITIATED',
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_transfers_status ON transfers(status);

CREATE TABLE IF NOT EXISTS transfer_events (
  id SERIAL PRIMARY KEY,
  transfer_id INTEGER NOT NULL REFERENCES transfers(id),
  type VARCHAR NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_transfer_events_transfer_id ON transfer_events(transfer_id);

CREATE TABLE IF NOT EXISTS kyc_documents (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR NOT NULL,
  doc_type VARCHAR NOT NULL,
  filename VARCHAR NOT NULL,
  encrypted_blob TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_kyc_documents_user_id ON kyc_documents(user_id);

CREATE TABLE IF NOT EXISTS audit_logs (
  id SERIAL PRIMARY KEY,
  trace_id VARCHAR NOT NULL,
  actor VARCHAR NOT NULL,
  action VARCHAR NOT NULL,
  entity VARCHAR NOT NULL,
  entity_id VARCHAR NOT NULL,
  details JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_audit_logs_trace ON audit_logs(trace_id);