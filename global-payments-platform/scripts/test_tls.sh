#!/usr/bin/env bash
set -euo pipefail
: "${ENDPOINT:?Set ENDPOINT=https://host:port}"
: "${CLIENT_CERT:?path to client cert}"
: "${CLIENT_KEY:?path to client key}"
: "${CA_CHAIN:?path to CA chain}"

echo "Testing openssl handshake..."
openssl s_client -connect "${ENDPOINT#https://}" -showcerts -tls1_3 -cert "$CLIENT_CERT" -key "$CLIENT_KEY" -CAfile "$CA_CHAIN" </dev/null | head -n 20

echo "Testing curl GET /ping..."
curl --http1.1 --tlsv1.3 --cert "$CLIENT_CERT" --key "$CLIENT_KEY" --cacert "$CA_CHAIN" "$ENDPOINT/ping" -v || true