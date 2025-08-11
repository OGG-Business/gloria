CREATE TABLE IF NOT EXISTS users (
  id BIGSERIAL PRIMARY KEY,
  subject VARCHAR(255) UNIQUE,
  email VARCHAR(255),
  role VARCHAR(64),
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS accounts (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id),
  iban VARCHAR(64),
  bic VARCHAR(16),
  display_name VARCHAR(255),
  sensitive_metadata BYTEA,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TYPE transfer_status AS ENUM ('INITIATED','PENDING','COMPLETED','FAILED');

CREATE TABLE IF NOT EXISTS transfers (
  id BIGSERIAL PRIMARY KEY,
  debtor_account_id BIGINT NOT NULL REFERENCES accounts(id),
  creditor_iban VARCHAR(64),
  creditor_bic VARCHAR(16),
  amount NUMERIC(18,2) NOT NULL,
  currency CHAR(3) NOT NULL,
  status transfer_status DEFAULT 'INITIATED',
  reference VARCHAR(255),
  pacs008_xml TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS transfer_events (
  id BIGSERIAL PRIMARY KEY,
  transfer_id BIGINT NOT NULL REFERENCES transfers(id),
  type VARCHAR(64) NOT NULL,
  payload TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS kyc_documents (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id),
  document_type VARCHAR(64) NOT NULL,
  encrypted_blob BYTEA NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_log (
  id BIGSERIAL PRIMARY KEY,
  correlation_id VARCHAR(128),
  actor_subject VARCHAR(255),
  action VARCHAR(128) NOT NULL,
  target VARCHAR(255) NOT NULL,
  details TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);