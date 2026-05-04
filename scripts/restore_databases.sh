#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <timestamp_backup> [catalog_db|customer_db|order_service_db|analytics_db]"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${ROOT_DIR}/backups/$1"
TARGET_DB="${2:-all}"

if [[ ! -d "${BACKUP_DIR}" ]]; then
  echo "Backup introuvable: ${BACKUP_DIR}"
  exit 1
fi

restore_db() {
  local database="$1"
  local container="$2"
  local user="$3"
  local sql_file="$4"

  if [[ ! -f "${sql_file}" ]]; then
    echo "Fichier de backup introuvable: ${sql_file}"
    exit 1
  fi

  echo "Restauration de ${database}..."
  docker exec -i "${container}" psql -U "${user}" -d "${database}" < "${sql_file}"
}

case "${TARGET_DB}" in
  all)
    restore_db "catalog_db" "catalog-db" "catalog_user" "${BACKUP_DIR}/catalog_db.sql"
    restore_db "customer_db" "customer-db" "postgres" "${BACKUP_DIR}/customer_db.sql"
    restore_db "order_service_db" "order-db" "order_service_user" "${BACKUP_DIR}/order_service_db.sql"
    restore_db "analytics_db" "analytics-db" "analytics_user" "${BACKUP_DIR}/analytics_db.sql"
    ;;
  catalog_db)
    restore_db "catalog_db" "catalog-db" "catalog_user" "${BACKUP_DIR}/catalog_db.sql"
    ;;
  customer_db)
    restore_db "customer_db" "customer-db" "postgres" "${BACKUP_DIR}/customer_db.sql"
    ;;
  order_service_db)
    restore_db "order_service_db" "order-db" "order_service_user" "${BACKUP_DIR}/order_service_db.sql"
    ;;
  analytics_db)
    restore_db "analytics_db" "analytics-db" "analytics_user" "${BACKUP_DIR}/analytics_db.sql"
    ;;
  *)
    echo "Base non supportee: ${TARGET_DB}"
    exit 1
    ;;
esac

echo "Restauration terminee."
