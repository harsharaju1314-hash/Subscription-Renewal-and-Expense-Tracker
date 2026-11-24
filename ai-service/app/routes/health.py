from flask import Blueprint, jsonify
from ai_service.config import settings

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "openai_model": settings.OPENAI_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL,
    })
