#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
ARCHIVE=${1:-openbank-transfers-$(date +%Y%m%d).tar.gz}
EXCLUDES=(
  --exclude='.git'
  --exclude='node_modules'
  --exclude='**/__pycache__'
  --exclude='.venv'
  --exclude='*.log'
)
cd "$ROOT_DIR"
tar -czf "$ARCHIVE" "${EXCLUDES[@]}" .
echo "Created $ARCHIVE"