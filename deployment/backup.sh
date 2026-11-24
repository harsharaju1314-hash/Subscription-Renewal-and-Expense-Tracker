#!/usr/bin/env bash
# ==============================================================================
# Production Backup Automation Script
# Backs up MySQL database, Redis persistence store, and FAISS vector indices.
# ==============================================================================
set -euo pipefail

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="${BACKUP_DIR:-/var/backups/subtrack}"
RETENTION_DAYS=7

MYSQL_CONTAINER="subtrack_mysql"
MYSQL_DATABASE="${MYSQL_DATABASE:-subscription_db}"
MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_PASSWORD="${MYSQL_ROOT_PASSWORD:-root_password}"

REDIS_CONTAINER="subtrack_redis"
REDIS_PASSWORD="${REDIS_PASSWORD:-redis_secure_pass_2026}"

mkdir -p "${BACKUP_DIR}/${TIMESTAMP}"
CURRENT_BACKUP="${BACKUP_DIR}/${TIMESTAMP}"

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting automated backup to ${CURRENT_BACKUP}..."

# 1. Backup MySQL Relational Database
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Dumping MySQL database: ${MYSQL_DATABASE}..."
docker exec "${MYSQL_CONTAINER}" \
  mysqldump --single-transaction --quick --lock-tables=false \
  -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" "${MYSQL_DATABASE}" | \
  gzip -9 > "${CURRENT_BACKUP}/mysql_${MYSQL_DATABASE}_${TIMESTAMP}.sql.gz"

# 2. Backup Redis Cache Store (Trigger BGSAVE and copy dump.rdb)
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Triggering Redis snapshot (BGSAVE)..."
docker exec "${REDIS_CONTAINER}" redis-cli -a "${REDIS_PASSWORD}" BGSAVE || true
sleep 3
docker cp "${REDIS_CONTAINER}:/data/dump.rdb" "${CURRENT_BACKUP}/redis_dump_${TIMESTAMP}.rdb" || true

# 3. Backup FAISS Vector Indices
if [ -d "./data/faiss_index" ]; then
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] Archiving FAISS vector database indices..."
  tar -czf "${CURRENT_BACKUP}/faiss_indices_${TIMESTAMP}.tar.gz" -C ./data faiss_index
fi

# 4. Compute SHA-256 Checksums
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Generating SHA-256 checksums..."
cd "${CURRENT_BACKUP}"
sha256sum * > SHA256SUMS.txt
cd - > /dev/null

# 5. Optional Upload to AWS S3
if [ -n "${S3_BACKUP_BUCKET:-}" ]; then
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] Uploading backup to S3 bucket: s3://${S3_BACKUP_BUCKET}/backups/${TIMESTAMP}/..."
  aws s3 cp --recursive "${CURRENT_BACKUP}/" "s3://${S3_BACKUP_BUCKET}/backups/${TIMESTAMP}/"
fi

# 6. Retention Policy Cleanup: Delete local backups older than RETENTION_DAYS
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Pruning local backups older than ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -maxdepth 1 -type d -mtime +${RETENTION_DAYS} -exec rm -rf {} +

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Backup successfully completed and verified!"
