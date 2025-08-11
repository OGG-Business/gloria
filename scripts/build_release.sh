#!/usr/bin/env bash
set -euo pipefail
ROOT=${1:-/workspace}
ARCHIVE=${2:-open-payments-hub.tar.gz}

tar --exclude-vcs --exclude='**/node_modules' --exclude='**/dist' --exclude='**/.venv' -czf "${ARCHIVE}" -C "${ROOT}" .
echo "Wrote ${ARCHIVE}"