from typing import List, Dict, Any
from langchain_core.documents import Document


def format_subscription_to_document(sub: Dict[str, Any], user_id: int) -> Document:
    """Transform a subscription record into a structured, highly searchable text document."""
    name = sub.get("name", "Unknown Subscription")
    cost = float(sub.get("cost", 0.0))
    monthly_cost = float(sub.get("monthly_cost", cost))
    cycle = sub.get("billing_cycle", "MONTHLY")
    category = sub.get("category", "General")
    renewal_date = sub.get("renewal_date", "N/A")
    utility = sub.get("utility_score", 5)
    essential_str = "Essential (cannot be cancelled)" if sub.get("is_essential") else "Optional (discretionary spend)"
    description = sub.get("description", "")

    page_content = (
        f"Subscription: {name}\n"
        f"Category: {category}\n"
        f"Cost: ${cost:.2f} per {cycle.lower()}\n"
        f"Normalized Monthly Spend: ${monthly_cost:.2f}/month\n"
        f"Annual Cost: ${monthly_cost * 12:.2f}/year\n"
        f"Renewal Date: {renewal_date}\n"
        f"Classification: {essential_str}\n"
        f"User Utility Rating: {utility} out of 10\n"
        f"Details: {description}\n"
    ).strip()

    metadata = {
        "user_id": user_id,
        "subscription_id": sub.get("id"),
        "name": name,
        "category": category,
        "cost": cost,
        "monthly_cost": monthly_cost,
        "billing_cycle": cycle,
        "renewal_date": renewal_date,
        "is_essential": sub.get("is_essential", False),
        "utility_score": utility,
    }

    return Document(page_content=page_content, metadata=metadata)


def build_documents_from_subscriptions(
    subscriptions: List[Dict[str, Any]], user_id: int
) -> List[Document]:
    return [format_subscription_to_document(s, user_id) for s in subscriptions]
