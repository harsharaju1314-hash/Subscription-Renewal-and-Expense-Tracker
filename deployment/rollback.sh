#!/usr/bin/env bash
# ==============================================================================
# Production Zero-Downtime Rollback Script
# Reverts services to a previous stable tag/commit or restores database state.
# ==============================================================================
set -euo pipefail

PREVIOUS_TAG="${1:-}"
BACKUP_TIMESTAMP="${2:-}"

if [ -z "${PREVIOUS_TAG}" ]; then
  echo "Usage: $0 <PREVIOUS_DOCKER_TAG_OR_GIT_COMMIT> [BACKUP_TIMESTAMP_FOR_DB_RESTORE]"
  echo "Example: $0 v1.0.4 20261124_153000"
  exit 1
fi

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Initiating rollback to release: ${PREVIOUS_TAG}..."

# 1. Stop current containers gracefully
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Gracefully stopping current backend and frontend..."
docker compose stop backend frontend analytics-service

# 2. Checkout previous release tag or update .env tag
if git rev-parse --verify "${PREVIOUS_TAG}" >/dev/null 2>&1; then
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] Checking out git revision: ${PREVIOUS_TAG}..."
  git checkout "${PREVIOUS_TAG}"
else
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] Setting IMAGE_TAG=${PREVIOUS_TAG} in environment..."
  export IMAGE_TAG="${PREVIOUS_TAG}"
fi

# 3. Optional Database Restoration from Backup
if [ -n "${BACKUP_TIMESTAMP}" ]; then
  BACKUP_FILE="/var/backups/subtrack/${BACKUP_TIMESTAMP}/mysql_subscription_db_${BACKUP_TIMESTAMP}.sql.gz"
  if [ -f "${BACKUP_FILE}" ]; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Restoring MySQL from backup: ${BACKUP_FILE}..."
    gunzip -c "${BACKUP_FILE}" | docker exec -i subtrack_mysql mysql -u"${MYSQL_USER:-root}" -p"${MYSQL_ROOT_PASSWORD:-root_password}" "${MYSQL_DATABASE:-subscription_db}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Database restored successfully."
  else
    echo "ERROR: Backup file ${BACKUP_FILE} not found!"
    exit 1
  fi
fi

# 4. Rebuild or pull containers for previous revision
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Re-launching services on target release..."
docker compose up -d --build backend analytics-service frontend

# 5. Verification & Healthcheck Polling
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Verifying service health..."
MAX_ATTEMPTS=20
ATTEMPT=0
HEALTHY=false

while [ ${ATTEMPT} -lt ${MAX_ATTEMPTS} ]; do
  ATTEMPT=$((ATTEMPT + 1))
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health/ready || echo "000")
  if [ "${STATUS}" = "200" ]; then
    HEALTHY=true
    break
  fi
  echo "Attempt ${ATTEMPT}/${MAX_ATTEMPTS}: Backend not ready yet (HTTP ${STATUS}). Retrying in 3s..."
  sleep 3
done

if [ "${HEALTHY}" = true ]; then
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] Rollback to ${PREVIOUS_TAG} SUCCEEDED! All systems healthy."
  exit 0
else
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] CRITICAL: Rollback failed healthchecks! Inspect logs with 'docker compose logs'."
  exit 1
fi
