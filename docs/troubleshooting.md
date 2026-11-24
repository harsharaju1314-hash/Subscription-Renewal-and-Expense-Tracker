# Operational Runbook & Troubleshooting Guide

This guide provides step-by-step diagnostic and remediation procedures for common operational incidents.

---

## 1. Database Connection Failures

### Symptoms
- FastAPI returns `503 Service Unavailable` on `/health/ready`.
- Logs report: `OperationalError: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server")`.

### Diagnostic Steps
1. Inspect MySQL container status:
   ```bash
   docker compose ps mysql
   ```
2. Check MySQL container logs:
   ```bash
   docker compose logs --tail=100 mysql
   ```
3. Test container internal ping:
   ```bash
   docker exec -it subtrack_mysql mysqladmin ping -u root -p
   ```

### Remediation
- **If container crashed:** Restart via `docker compose restart mysql`.
- **If disk full:** Check disk space with `df -h`. Free space by pruning Docker cache: `docker system prune -f`.
- **If corrupted tables:** Run recovery:
   ```bash
   docker exec -it subtrack_mysql mysqlcheck -u root -p --auto-repair --all-databases
   ```
- **If unrecoverable:** Restore the latest backup using `deployment/rollback.sh <COMMIT> <BACKUP_TIMESTAMP>`.

---

## 2. Redis Outages & Fallback Behavior

### Symptoms
- Logs report: `Redis connection failed (...); using in-memory cache fallback.`
- Cache hit ratio metrics in Grafana drop or show in-memory backend.

### Expected Behavior
- The application automatically falls back to an in-memory Least-Recently-Used (LRU) cache dictionary without throwing 500 errors to clients.
- Rate limiting falls back to process-level tracking.

### Remediation
1. Inspect Redis status:
   ```bash
   docker compose ps redis
   docker compose logs --tail=50 redis
   ```
2. Restart Redis container:
   ```bash
   docker compose restart redis
   ```
3. Verify Redis responsiveness:
   ```bash
   docker exec -it subtrack_redis redis-cli ping
   ```
   FastAPI will automatically reconnect on the subsequent request.

---

## 3. OpenAI API / LLM Outages & Timeouts

### Symptoms
- AI Assistant queries take longer than 5 seconds or fail with HTTP 504 Gateway Timeout.
- Logs display: `OpenAI API connection error` or `RateLimitError`.

### Expected Behavior
- The `ai_client` catches upstream LLM exceptions and delivers a graceful deterministic fallback response containing exact SQL-computed expense figures and source records.
- User requests complete without crashing.

### Remediation
1. Verify API Key validity:
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```
2. Check OpenAI Service Health: `https://status.openai.com`
3. If quota exceeded: Top up the developer balance or temporarily switch the model in `.env` (`OPENAI_MODEL=gpt-4o-mini`).

---

## 4. High Error Rate / Slow Response Runbook

1. Check real-time Prometheus alerts:
   ```bash
   curl -s http://localhost:9090/api/v1/alerts | jq .
   ```
2. Check active concurrent requests:
   ```bash
   curl -s http://localhost:8000/metrics | grep active_requests
   ```
3. Identify slow database queries:
   ```bash
   docker exec -it subtrack_mysql mysql -u root -p -e "SHOW FULL PROCESSLIST;"
   ```
4. If application memory exceeds threshold:
   ```bash
   docker compose restart backend analytics-service
   ```
