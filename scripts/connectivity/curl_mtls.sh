#!/usr/bin/env bash
set -euo pipefail
URL=${1:?}
CLIENT_CRT=${2:?}
CLIENT_KEY=${3:?}
CA_CRT=${4:?}
shift 4
curl -v "$URL" --cert "$CLIENT_CRT" --key "$CLIENT_KEY" --cacert "$CA_CRT" "$@"