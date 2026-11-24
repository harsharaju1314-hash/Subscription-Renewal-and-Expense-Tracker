from flask import Blueprint, request, jsonify
from ai_service.prompts.financial_prompts import SUMMARIZE_PROMPT_TEMPLATE

summarize_bp = Blueprint("summarize", __name__)


@summarize_bp.route("/ai/summarize", methods=["POST"])
def summarize():
    data = request.get_json(force=True) or {}
    subscriptions = data.get("subscriptions", [])
    monthly_spend = float(data.get("monthly_spend", 0.0))
    annual_spend = monthly_spend * 12.0

    sub_lines = [
        f"- {s.get('name')}: ${float(s.get('cost', 0)):.2f} ({s.get('billing_cycle')}) [{s.get('category')}]"
        for s in subscriptions
    ]
    sub_text = "\n".join(sub_lines) if sub_lines else "No subscriptions."

    summary = (
        f"Portfolio overview: You maintain {len(subscriptions)} active subscriptions with a total recurring run-rate "
        f"of ${monthly_spend:.2f}/month (${annual_spend:.2f}/year). "
        f"Top categories represent the primary cost drivers."
    )

    highlights = [
        f"Total monthly subscription run-rate: ${monthly_spend:.2f}",
        f"Projected 12-month expense: ${annual_spend:.2f}",
        f"{len(subscriptions)} active subscription accounts monitored",
    ]

    recommendations = [
        "Audit optional subscriptions with low utility scores to reclaim recurring cashflow.",
        "Consider switching frequently used monthly services to annual plans for discounts.",
        "Run the automated Mixed-Integer Linear Program optimizer to align with your monthly budget cap.",
    ]

    return jsonify({
        "summary": summary,
        "highlights": highlights,
        "monthly_total": monthly_spend,
        "annual_projection": annual_spend,
        "recommendations": recommendations,
    })
