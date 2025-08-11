#!/usr/bin/env bash
set -euo pipefail
CERT_DIR=${1:-./certs}
mkdir -p "$CERT_DIR"

if [ ! -f "$CERT_DIR/dev-key.pem" ]; then
  echo "Generating dev self-signed cert..."
  openssl req -x509 -newkey rsa:4096 -nodes -keyout "$CERT_DIR/dev-key.pem" -out "$CERT_DIR/dev-cert.pem" -days 365 -subj "/CN=localhost"
fi

echo "Place bank-provided CA and client certs under ./secrets/swift as:"
echo "  client_key.pem, client_cert.pem, ca_chain.pem"