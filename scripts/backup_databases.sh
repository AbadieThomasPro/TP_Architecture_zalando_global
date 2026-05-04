#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_ROOT="${ROOT_DIR}/backups"
TIMESTAMP="$(date +"%Y%m%d_%H%M%S")"
BACKUP_DIR="${BACKUP_ROOT}/${TIMESTAMP}"

mkdir -p "${BACKUP_DIR}"

backup_db() {
  local container="$1"
  local user="$2"
  local database="$3"
  local output_file="$4"

  echo "Sauvegarde de ${database}..."
  docker exec "${container}" pg_dump -U "${user}" -d "${database}" --clean --if-exists --no-owner --no-privileges \
    > "${output_file}"
}

backup_db "catalog-db" "catalog_user" "catalog_db" "${BACKUP_DIR}/catalog_db.sql"
backup_db "customer-db" "postgres" "customer_db" "${BACKUP_DIR}/customer_db.sql"
backup_db "order-db" "order_service_user" "order_service_db" "${BACKUP_DIR}/order_service_db.sql"
backup_db "analytics-db" "analytics_user" "analytics_db" "${BACKUP_DIR}/analytics_db.sql"

cat > "${BACKUP_DIR}/README.txt" <<EOF
Backup cree le ${TIMESTAMP}

Fichiers:
- catalog_db.sql
- customer_db.sql
- order_service_db.sql
- analytics_db.sql

Restauration complete:
./scripts/restore_databases.sh ${TIMESTAMP}

Restauration d'une seule base:
./scripts/restore_databases.sh ${TIMESTAMP} customer_db
EOF

echo "Backup termine dans ${BACKUP_DIR}"
