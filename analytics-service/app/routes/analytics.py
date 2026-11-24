import logging
from flask import Blueprint, request, jsonify, Response
from analytics_service.app.config import settings
from analytics_service.app.services.calculator import FinancialCalculator
from analytics_service.app.services.exporter import generate_expense_csv

logger = logging.getLogger(__name__)
analytics_bp = Blueprint("analytics", __name__)


def verify_internal_auth() -> bool:
    """Validate internal service secret for secure inter-service communication."""
    secret = request.headers.get("X-Internal-Secret")
    if settings.ENVIRONMENT == "testing":
        return True
    if not secret or secret != settings.INTERNAL_SERVICE_SECRET:
        return False
    return True


@analytics_bp.before_request
def check_auth():
    if request.path == "/health":
        return None
    if not verify_internal_auth():
        return jsonify({"error": "Unauthorized: Invalid internal service credentials."}), 401


@analytics_bp.route("/analytics/aggregate", methods=["POST"])
def aggregate_summary():
    data = request.get_json(force=True) or {}
    subscriptions = data.get("subscriptions", [])
    monthly_budget = float(data.get("monthly_budget", 250.00))

    summary = FinancialCalculator.calculate_summary(subscriptions, monthly_budget)
    return jsonify(summary)


@analytics_bp.route("/analytics/breakdown", methods=["POST"])
def category_breakdown():
    data = request.get_json(force=True) or {}
    subscriptions = data.get("subscriptions", [])

    breakdown = FinancialCalculator.calculate_category_breakdown(subscriptions)
    return jsonify(breakdown)


@analytics_bp.route("/analytics/redundancy", methods=["POST"])
def detect_redundancies():
    data = request.get_json(force=True) or {}
    subscriptions = data.get("subscriptions", [])

    result = FinancialCalculator.detect_redundancies(subscriptions)
    return jsonify(result)


@analytics_bp.route("/analytics/report", methods=["POST"])
def generate_full_report():
    data = request.get_json(force=True) or {}
    subscriptions = data.get("subscriptions", [])
    monthly_budget = float(data.get("monthly_budget", 250.00))

    summary = FinancialCalculator.calculate_summary(subscriptions, monthly_budget)
    breakdown = FinancialCalculator.calculate_category_breakdown(subscriptions)
    redundancies = FinancialCalculator.detect_redundancies(subscriptions)

    report = {
        "summary": summary,
        "category_breakdown": breakdown["categories"],
        "redundancies": redundancies,
        "report_generated_at": data.get("timestamp"),
    }
    return jsonify(report)


@analytics_bp.route("/analytics/export-csv", methods=["POST"])
def export_csv():
    data = request.get_json(force=True) or {}
    subscriptions = data.get("subscriptions", [])

    csv_content = generate_expense_csv(subscriptions)
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=expense_analytics_report.csv"}
    )
