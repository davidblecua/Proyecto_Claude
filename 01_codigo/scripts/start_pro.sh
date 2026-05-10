#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
echo "Arrancando entorno PRO (puerto 8002)..."
docker compose -f docker-compose.pro.yml up --build -d
echo "PRO disponible en http://localhost:8002"
