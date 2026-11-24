from flask import Blueprint, jsonify
from analytics_service.app.config import settings

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def healthcheck():
    return jsonify({
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "environment": settings.ENVIRONMENT,
        "port": settings.PORT,
    })
