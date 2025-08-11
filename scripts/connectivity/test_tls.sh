#!/usr/bin/env bash
set -euo pipefail
URL=${1:?Usage: $0 https://host:port/path client.crt client.key ca.crt}
CLIENT_CRT=${2:?}
CLIENT_KEY=${3:?}
CA_CRT=${4:?}
HOSTPORT=$(echo "$URL" | sed -E 's#https?://([^/]+).*#\1#')
echo | openssl s_client -connect "$HOSTPORT" -cert "$CLIENT_CRT" -key "$CLIENT_KEY" -CAfile "$CA_CRT" -alpn h2 -tls1_3 -brief