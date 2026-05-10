#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
echo "Arrancando entorno PRE (puerto 8001)..."
docker compose -f docker-compose.pre.yml up --build -d
echo "PRE disponible en http://localhost:8001"
