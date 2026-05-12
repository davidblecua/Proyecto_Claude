#!/usr/bin/env bash
# start_demo.sh — Arranca el entorno demo de RentaMaq (DEV)
# Uso: bash start_demo.sh [dev|pre|pro]

set -e

ENV=${1:-dev}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

case "$ENV" in
  dev) PORT=8080 ;;
  pre) PORT=8001 ;;
  pro) PORT=8002 ;;
  *) echo "Entorno no válido: $ENV (usa dev|pre|pro)"; exit 1 ;;
esac

echo ""
echo "=== RentaMaq Demo — entorno: ${ENV^^} ==="
echo ""

echo "[1/2] Cargando datos demo..."
(cd "$BACKEND_DIR" && python seeds/seed_demo.py --env "$ENV")

echo ""
echo "[2/2] Arrancando servidor en http://localhost:$PORT"
echo ""
echo "Credenciales demo:"
echo "  Propietario : david@demo.com   / Demo1234!"
echo "  Cliente     : cliente@demo.com / Demo1234!"
echo "  Admin       : admin@demo.com   / Demo1234!"
echo ""
echo "Pulsa Ctrl+C para detener."
echo ""

export APP_ENV="$ENV"
cd "$BACKEND_DIR"
python -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --reload
