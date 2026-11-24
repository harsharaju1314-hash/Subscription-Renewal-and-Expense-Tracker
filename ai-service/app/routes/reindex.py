from flask import Blueprint, request, jsonify
from ai_service.rag.vector_store import vector_manager

reindex_bp = Blueprint("reindex", __name__)


@reindex_bp.route("/ai/reindex", methods=["POST"])
def reindex():
    data = request.get_json(force=True) or {}
    user_id = data.get("user_id")
    subscriptions = data.get("subscriptions", [])

    if not user_id:
        return jsonify({"error": "Missing user_id parameter."}), 400

    count = vector_manager.index_subscriptions(user_id, subscriptions)
    return jsonify({
        "status": "success",
        "user_id": user_id,
        "indexed_documents_count": count,
    })
