import json
import logging
import time
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Context variable tracking correlation ID per async request
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")


class StructuredJSONFormatter(logging.Formatter):
    """Custom logging formatter that renders structured JSON records with correlation IDs."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": correlation_id_ctx.get(""),
            "module": record.module,
            "line": record.lineno,
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Assigns or extracts X-Correlation-ID for distributed tracing across services."""

    async def dispatch(self, request: Request, call_next):
        corr_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        token = correlation_id_ctx.set(corr_id)
        try:
            response: Response = await call_next(request)
            response.headers["X-Correlation-ID"] = corr_id
            return response
        finally:
            correlation_id_ctx.reset(token)


def setup_structured_logging():
    """Configure root logger with structured JSON formatting."""
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredJSONFormatter())
    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)
