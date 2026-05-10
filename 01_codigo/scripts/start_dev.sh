#!/bin/bash
echo "Arrancando entorno DEV (puerto 8080)..."
echo "DEV corre sin Docker. Lanzando uvicorn directamente."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../backend"
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
