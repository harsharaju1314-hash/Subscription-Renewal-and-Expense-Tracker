import logging
from flask import Flask, jsonify
from flask_cors import CORS

from ai_service.config import settings
from ai_service.routes.chat import chat_bp
from ai_service.routes.reindex import reindex_bp
from ai_service.routes.summarize import summarize_bp
from ai_service.routes.health import health_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ai_service")


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    # Register Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(reindex_bp)
    app.register_blueprint(summarize_bp)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(500)
    def internal_error(e):
        logger.error("Internal Server Error: %s", e)
        return jsonify({"error": "Internal AI inference error."}), 500

    return app


app = create_app()

if __name__ == "__main__":
    logger.info("Starting %s on %s:%d...", settings.SERVICE_NAME, settings.HOST, settings.PORT)
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
