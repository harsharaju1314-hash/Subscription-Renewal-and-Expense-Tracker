import time
import os

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# HTTP metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP request count partitioned by method, endpoint, and status",
    ["method", "endpoint", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)
ACTIVE_REQUESTS = Gauge(
    "active_requests",
    "Number of concurrent active requests currently being processed",
)

# Database & Cache metrics
DB_QUERY_LATENCY = Histogram(
    "database_query_duration_seconds",
    "Database query execution latency in seconds",
    ["operation"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5],
)
CACHE_HITS = Counter(
    "redis_cache_hits_total",
    "Total count of Redis cache hits",
)
CACHE_MISSES = Counter(
    "redis_cache_misses_total",
    "Total count of Redis cache misses",
)

# AI & RAG metrics
AI_LATENCY = Histogram(
    "ai_response_duration_seconds",
    "Latency of AI query inferences and RAG vector search in seconds",
    buckets=[0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0],
)
LLM_FAILURES = Counter(
    "llm_request_failures_total",
    "Count of external LLM API failures that triggered graceful fallback",
)

# System and Uptime metrics
SERVICE_UPTIME = Gauge(
    "service_uptime_seconds",
    "Elapsed system service uptime in seconds",
)
SYSTEM_MEMORY_USAGE = Gauge(
    "system_memory_usage_bytes",
    "Resident set memory used by process in bytes",
)
SYSTEM_CPU_PERCENT = Gauge(
    "system_cpu_percent",
    "Process CPU utilization percentage",
)

SERVICE_START_TIME = time.time()


def update_system_metrics():
    """Sample real CPU, memory, and uptime metrics."""
    try:
        SERVICE_UPTIME.set(time.time() - SERVICE_START_TIME)
        if PSUTIL_AVAILABLE:
            process = psutil.Process(os.getpid())
            SYSTEM_MEMORY_USAGE.set(process.memory_info().rss)
            SYSTEM_CPU_PERCENT.set(process.cpu_percent(interval=None))
    except Exception:
        pass


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Exclude metrics endpoint itself from recursion
        if request.url.path.endswith("/metrics"):
            return await call_next(request)

        ACTIVE_REQUESTS.inc()
        start_time = time.time()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration = time.time() - start_time
            ACTIVE_REQUESTS.dec()

            # Normalize endpoint path for low-cardinality Prometheus labels
            path = request.url.path
            for prefix in ["/api/v1", "/api"]:
                if path.startswith(prefix):
                    path = path[len(prefix):]
                    break
            # Group resource IDs like /subscriptions/123 -> /subscriptions/{id}
            parts = path.split("/")
            normalized_parts = [
                "{id}" if part.isdigit() else part for part in parts
            ]
            normalized_path = "/".join(normalized_parts) or "/"

            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=normalized_path,
                status_code=str(status_code),
            ).inc()
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=normalized_path,
            ).observe(duration)
            update_system_metrics()


def prometheus_metrics_response() -> Response:
    update_system_metrics()
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
