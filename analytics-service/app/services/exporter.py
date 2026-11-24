import csv
import io
from typing import List, Dict, Any
from decimal import Decimal
from analytics_service.app.services.calculator import monthly_equivalent, to_decimal


def generate_expense_csv(subscriptions: List[Dict[str, Any]]) -> str:
    """Generate standard formatted CSV report of user subscriptions and costs."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow([
        "Subscription ID",
        "Name",
        "Category",
        "Billing Cycle",
        "Cost",
        "Currency",
        "Monthly Equivalent",
        "Annual Equivalent",
        "Renewal Date",
        "Status",
        "Utility Score",
        "Is Essential",
        "Payment Method"
    ])

    for s in subscriptions:
        cost_dec = to_decimal(s.get("cost", 0.0))
        cycle = str(s.get("billing_cycle", "MONTHLY"))
        m_equiv = monthly_equivalent(cost_dec, cycle)
        a_equiv = m_equiv * Decimal("12")

        writer.writerow([
            s.get("id", ""),
            s.get("name", ""),
            s.get("category_name", "General"),
            cycle,
            f"{float(cost_dec):.2f}",
            s.get("currency", "USD"),
            f"{float(m_equiv):.2f}",
            f"{float(a_equiv):.2f}",
            s.get("renewal_date", ""),
            s.get("status", "ACTIVE"),
            s.get("utility_score", 5),
            "YES" if s.get("is_essential") else "NO",
            s.get("payment_method", "N/A"),
        ])

    return output.getvalue()
