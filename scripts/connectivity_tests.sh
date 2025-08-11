#!/usr/bin/env bash
set -euo pipefail

CERT=${CERT:-secrets/client.crt}
KEY=${KEY:-secrets/client.key}
CA=${CA:-secrets/ca.crt}
HOST=${HOST:-bank.example.com}
URL=${URL:-https://bank.example.com/ping}

openssl s_client -connect ${HOST}:443 -servername ${HOST} -cert ${CERT} -key ${KEY} -CAfile ${CA} </dev/null | head -n 30

curl --cert ${CERT} --key ${KEY} --cacert ${CA} ${URL} -v