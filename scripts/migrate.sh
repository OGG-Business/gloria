#!/usr/bin/env bash
set -euo pipefail
DIR=$(cd "$(dirname "$0")/.." && pwd)
 docker run --rm \
  -v "$DIR/db/migrations":/flyway/sql \
  flyway/flyway:10.17.0 \
  -url=jdbc:postgresql://localhost:5432/transfers -user=postgres -password=postgres migrate