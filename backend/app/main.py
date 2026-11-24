from contextlib import asynccontextmanager
import logging
import time
from fastapi import FastAPI, Request, status, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import Base, engine, SessionLocal, get_db
from backend.app.core.cache import cache
from backend.app.core.logging_config import CorrelationIdMiddleware, setup_structured_logging
from backend.app.core.metrics import PrometheusMiddleware, prometheus_metrics_response
from backend.app.models.category import Category
from backend.app.models.role import Role
from backend.app.routers import (
    auth_router,
    subscriptions_router,
    categories_router,
    analytics_router,
    optimization_router,
    ai_router,
    expenses_router,
    renewals_router,
    admin_router,
)

# Configure structured JSON logging
setup_structured_logging()
logger = logging.getLogger("backend")


def seed_default_roles():
    """Ensure standard roles (USER, ANALYST, ADMIN) exist in database."""
    default_roles = [
        {"name": "USER", "description": "Manage personal subscriptions and view personal reports."},
        {"name": "ANALYST", "description": "Access authorized aggregated expense reports."},
        {"name": "ADMIN", "description": "Manage users and monitor application operations."},
    ]
    db = SessionLocal()
    try:
        for r_data in default_roles:
            exists = db.query(Role).filter(Role.name == r_data["name"]).first()
            if not exists:
                db.add(Role(**r_data))
        db.commit()
    except Exception as e:
        logger.error("Role seed error: %s", e)
        db.rollback()
    finally:
        db.close()


def seed_default_categories():
    """Ensure standard financial categories are present in database."""
    default_categories = [
        {"name": "Streaming & Entertainment", "description": "Video and media streaming services", "icon": "live_tv", "color": "#ef4444"},
        {"name": "Music & Audio", "description": "Music streaming, audiobooks, podcasts", "icon": "headphones", "color": "#10b981"},
        {"name": "Software & Developer Tools", "description": "IDEs, GitHub, developer cloud services", "icon": "code", "color": "#6366f1"},
        {"name": "Cloud & Infrastructure", "description": "AWS, GCP, Azure, VPS, domain hosting", "icon": "cloud", "color": "#0ea5e9"},
        {"name": "Productivity & Office", "description": "Notion, Google Workspace, Microsoft 365", "icon": "work", "color": "#f59e0b"},
        {"name": "Fitness & Health", "description": "Gym, fitness tracking apps, health subscriptions", "icon": "fitness_center", "color": "#ec4899"},
        {"name": "Shopping & Delivery", "description": "Amazon Prime, Instacart, grocery deliveries", "icon": "shopping_cart", "color": "#8b5cf6"},
        {"name": "News & Learning", "description": "Medium, NYTimes, Coursera, news subscriptions", "icon": "menu_book", "color": "#14b8a6"},
    ]
    db = SessionLocal()
    try:
        for cat_data in default_categories:
            exists = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if not exists:
                cat = Category(**cat_data)
                db.add(cat)
        db.commit()
        logger.info("Default financial categories initialized.")
    except Exception as e:
        logger.error("Category seed error: %s", e)
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.ENVIRONMENT != "testing":
        logger.info("Starting up %s v%s...", settings.PROJECT_NAME, settings.VERSION)
        Base.metadata.create_all(bind=engine)
        seed_default_roles()
        seed_default_categories()
        logger.info("Database schemas and seed catalogs verified.")
    yield
    logger.info("Shutting down %s...", settings.PROJECT_NAME)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade AI-Powered Subscription & Expense Analytics Platform API.",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Middlewares
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(PrometheusMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Prometheus Metrics Endpoint
@app.get("/metrics", tags=["Monitoring"])
def metrics():
    """Prometheus exposition format metrics exporter."""
    return prometheus_metrics_response()


# Health Checks (Liveness and Readiness)
@app.get("/health", tags=["Health"])
@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def healthcheck():
    """System health overview and dependency readiness check."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "redis_connected": cache.is_redis_connected,
        "database": "connected",
    }


@app.get("/health/live", tags=["Health"])
def liveness():
    """Kubernetes / Docker container liveness probe."""
    return {"status": "alive", "timestamp": time.time()}


@app.get("/health/ready", tags=["Health"])
def readiness(db: Session = Depends(get_db)):
    """Kubernetes / Docker container readiness probe."""
    db_ok = True
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    if not db_ok:
        return JSONResponse(status_code=503, content={"status": "not_ready", "database": "unavailable"})
    return {
        "status": "ready",
        "database": "connected",
        "redis_connected": cache.is_redis_connected,
        "timestamp": time.time(),
    }


# Include Routers at /api/v1 (Canonical) and /api (Compatibility)
for prefix in ["/api/v1", "/api"]:
    app.include_router(auth_router, prefix=prefix)
    app.include_router(categories_router, prefix=prefix)
    app.include_router(subscriptions_router, prefix=prefix)
    app.include_router(renewals_router, prefix=prefix)
    app.include_router(expenses_router, prefix=prefix)
    app.include_router(analytics_router, prefix=prefix)
    app.include_router(optimization_router, prefix=prefix)
    app.include_router(ai_router, prefix=prefix)
    app.include_router(admin_router, prefix=prefix)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception for %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred."},
    )
