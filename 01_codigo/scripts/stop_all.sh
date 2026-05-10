#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
echo "Deteniendo todos los entornos..."
docker compose -f docker-compose.dev.yml down 2>/dev/null || true
docker compose -f docker-compose.pre.yml down 2>/dev/null || true
docker compose -f docker-compose.pro.yml down 2>/dev/null || true
echo "Todos los entornos detenidos."
