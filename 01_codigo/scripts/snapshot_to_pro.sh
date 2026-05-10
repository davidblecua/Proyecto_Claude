#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
mkdir -p backups

TIMESTAMP=$(date +%Y%m%d_%H%M)
SNAPSHOT_FILE="backups/snapshot_pro_${TIMESTAMP}.sql"

echo "Creando snapshot de PRE → PRO..."
echo "Volcando BD de PRE..."
docker exec rentamaq_db_pre pg_dump -U rentamaq_pre rentamaq_pre > "$SNAPSHOT_FILE"

echo "Restaurando en PRO..."
docker exec -i rentamaq_db_pro psql -U rentamaq_pro rentamaq_pro < "$SNAPSHOT_FILE"

echo "Snapshot completado: $SNAPSHOT_FILE"
echo "PRO actualizado con datos de PRE."
