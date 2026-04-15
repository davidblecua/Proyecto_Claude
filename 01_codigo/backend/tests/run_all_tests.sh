#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# RentaMaq — Suite completa de tests
# Ejecutar desde: 01_codigo/backend/
#   bash tests/run_all_tests.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

cd "$BACKEND_DIR"

export APP_ENV=test

echo "============================================================"
echo "  RentaMaq — Suite completa de tests"
echo "  $(date)"
echo "============================================================"
echo ""

python -m pytest tests/ -v \
    --tb=short \
    -q \
    2>&1

echo ""
echo "============================================================"
echo "  Fin de la suite"
echo "============================================================"
