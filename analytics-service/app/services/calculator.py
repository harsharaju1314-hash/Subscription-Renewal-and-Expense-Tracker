from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional
from datetime import date, timedelta


def to_decimal(val: Any) -> Decimal:
    """Safe conversion to Decimal for financial math."""
    if isinstance(val, Decimal):
        return val
    try:
        return Decimal(str(val))
    except Exception:
        return Decimal("0.00")


def monthly_equivalent(cost: Decimal, billing_cycle: str) -> Decimal:
    """Compute exact monthly equivalent cost using Decimal arithmetic."""
    c = to_decimal(cost)
    cycle = billing_cycle.upper() if billing_cycle else "MONTHLY"

    if cycle in ("MONTHLY", "MONTH"):
        return c.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    elif cycle in ("ANNUAL", "YEARLY", "ANNUALLY"):
        return (c / Decimal("12")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    elif cycle in ("QUARTERLY", "QUARTER"):
        return (c / Decimal("3")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    elif cycle in ("WEEKLY", "WEEK"):
        return ((c * Decimal("52")) / Decimal("12")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return c.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class FinancialCalculator:
    """Performs deterministic financial calculations and aggregation for subscription expense analysis."""

    @staticmethod
    def calculate_summary(subscriptions: List[Dict[str, Any]], monthly_budget: float = 250.00) -> Dict[str, Any]:
        active = [s for s in subscriptions if s.get("status", "ACTIVE").upper() == "ACTIVE"]

        total_monthly_dec = Decimal("0.00")
        sub_details = []

        for s in active:
            cost_dec = to_decimal(s.get("cost", 0.0))
            cycle = str(s.get("billing_cycle", "MONTHLY"))
            m_equiv = monthly_equivalent(cost_dec, cycle)
            total_monthly_dec += m_equiv

            sub_details.append({
                **s,
                "monthly_cost": float(m_equiv),
                "cost_dec": cost_dec,
            })

        total_monthly = float(total_monthly_dec)
        total_annual = float((total_monthly_dec * Decimal("12")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

        budget_dec = to_decimal(monthly_budget)
        utilization = float(((total_monthly_dec / budget_dec) * Decimal("100")).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)) if budget_dec > 0 else 0.0

        today = date.today()
        upcoming_7d = []
        upcoming_30d = []

        for s in active:
            ren_str = s.get("renewal_date")
            if ren_str:
                try:
                    ren_dt = date.fromisoformat(str(ren_str)[:10])
                    if today <= ren_dt <= (today + timedelta(days=7)):
                        upcoming_7d.append(s)
                    if today <= ren_dt <= (today + timedelta(days=30)):
                        upcoming_30d.append(s)
                except Exception:
                    pass

        # Potential savings: non-essential and utility <= 4
        savings_dec = sum(
            (to_decimal(s["monthly_cost"]) for s in sub_details
             if not s.get("is_essential", False) and int(s.get("utility_score", 5)) <= 4),
            Decimal("0.00")
        )

        most_expensive = None
        if sub_details:
            sorted_subs = sorted(sub_details, key=lambda x: x["monthly_cost"], reverse=True)
            top = sorted_subs[0]
            most_expensive = {
                "id": top.get("id"),
                "name": top.get("name"),
                "cost": float(top["cost_dec"]),
                "billing_cycle": top.get("billing_cycle"),
                "monthly_equivalent": round(top["monthly_cost"], 2),
                "category_name": top.get("category_name", "General"),
            }

        return {
            "total_monthly_spend": round(total_monthly, 2),
            "total_annual_spend": round(total_annual, 2),
            "active_subscriptions_count": len(active),
            "total_subscriptions_count": len(subscriptions),
            "upcoming_renewals_7d_count": len(upcoming_7d),
            "upcoming_renewals_30d_count": len(upcoming_30d),
            "monthly_budget": round(monthly_budget, 2),
            "budget_utilization_pct": round(utilization, 1),
            "potential_monthly_savings": float(savings_dec.quantize(Decimal("0.01"))),
            "most_expensive_subscription": most_expensive,
        }

    @staticmethod
    def calculate_category_breakdown(subscriptions: List[Dict[str, Any]]) -> Dict[str, Any]:
        active = [s for s in subscriptions if s.get("status", "ACTIVE").upper() == "ACTIVE"]
        categories: Dict[str, Dict[str, Any]] = {}
        total_monthly_dec = Decimal("0.00")

        for s in active:
            cost_dec = to_decimal(s.get("cost", 0.0))
            cycle = str(s.get("billing_cycle", "MONTHLY"))
            m_equiv = monthly_equivalent(cost_dec, cycle)
            total_monthly_dec += m_equiv

            cat_name = s.get("category_name") or "Uncategorized"
            color = s.get("category_color") or "#6366f1"
            icon = s.get("category_icon") or "category"

            if cat_name not in categories:
                categories[cat_name] = {
                    "category_name": cat_name,
                    "color": color,
                    "icon": icon,
                    "monthly_spend_dec": Decimal("0.00"),
                    "count": 0,
                }
            categories[cat_name]["monthly_spend_dec"] += m_equiv
            categories[cat_name]["count"] += 1

        items = []
        for cat_name, data in categories.items():
            cat_spend = data["monthly_spend_dec"]
            pct = float(((cat_spend / total_monthly_dec) * Decimal("100")).quantize(Decimal("0.1"))) if total_monthly_dec > 0 else 0.0
            items.append({
                "category_name": cat_name,
                "monthly_spend": float(cat_spend.quantize(Decimal("0.01"))),
                "annual_spend": float((cat_spend * Decimal("12")).quantize(Decimal("0.01"))),
                "percentage_of_total": pct,
                "subscription_count": data["count"],
                "color": data["color"],
                "icon": data["icon"],
            })

        items.sort(key=lambda x: x["monthly_spend"], reverse=True)
        return {
            "categories": items,
            "total_monthly_spend": float(total_monthly_dec.quantize(Decimal("0.01"))),
        }

    @staticmethod
    def detect_redundancies(subscriptions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect potentially redundant subscriptions, category clutter, and low-utility expenses."""
        active = [s for s in subscriptions if s.get("status", "ACTIVE").upper() == "ACTIVE"]

        # Category clutter (more than 1 subscription in entertainment/streaming, etc.)
        cat_counts: Dict[str, List[Dict[str, Any]]] = {}
        for s in active:
            cat = s.get("category_name", "General")
            cat_counts.setdefault(cat, []).append(s)

        redundancy_flags = []
        for cat, items in cat_counts.items():
            if len(items) > 1 and cat.lower() in ("streaming", "streaming & entertainment", "music", "music & audio"):
                names = [it.get("name") for it in items]
                total_cat_spend = sum(
                    float(monthly_equivalent(to_decimal(it.get("cost", 0)), str(it.get("billing_cycle", "MONTHLY"))))
                    for it in items
                )
                redundancy_flags.append({
                    "category": cat,
                    "issue": f"Multiple active {cat} subscriptions ({', '.join(names)})",
                    "count": len(items),
                    "combined_monthly_spend": round(total_cat_spend, 2),
                    "recommendation": f"Consider consolidating {cat} subscriptions to save up to ${round(total_cat_spend * 0.5, 2)}/month.",
                })

        # Low utility subscriptions (utility <= 4 and non-essential)
        low_utility = []
        for s in active:
            util = int(s.get("utility_score", 5))
            is_ess = bool(s.get("is_essential", False))
            if util <= 4 and not is_ess:
                m = float(monthly_equivalent(to_decimal(s.get("cost", 0)), str(s.get("billing_cycle", "MONTHLY"))))
                low_utility.append({
                    "id": s.get("id"),
                    "name": s.get("name"),
                    "monthly_cost": round(m, 2),
                    "utility_score": util,
                    "category": s.get("category_name", "General"),
                    "recommendation": "Review for cancellation due to low utilization rating.",
                })

        return {
            "category_redundancies": redundancy_flags,
            "low_utility_subscriptions": low_utility,
            "total_potential_savings": round(sum(it["monthly_cost"] for it in low_utility), 2),
        }
