from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional
from datetime import date, timedelta


def to_decimal(val: Any) -> Decimal:
    if isinstance(val, Decimal):
        return val
    try:
        return Decimal(str(val))
    except Exception:
        return Decimal("0.00")


def monthly_equiv(cost: Decimal, billing_cycle: str) -> Decimal:
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


# -------------------------------------------------------------------------
# Deterministic Financial Tools for LangChain / AI Agent
# -------------------------------------------------------------------------

def tool_calculate_monthly_spend(subscriptions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculates deterministic monthly and annual subscription expenses using Decimal arithmetic."""
    active = [s for s in subscriptions if s.get("status", "ACTIVE").upper() == "ACTIVE"]
    monthly_sum = Decimal("0.00")
    for s in active:
        monthly_sum += monthly_equiv(to_decimal(s.get("cost", 0)), str(s.get("billing_cycle", "MONTHLY")))

    annual_sum = monthly_sum * Decimal("12")
    return {
        "tool_name": "calculate_monthly_spend",
        "active_subscription_count": len(active),
        "total_monthly_spend": float(monthly_sum.quantize(Decimal("0.01"))),
        "total_annual_spend": float(annual_sum.quantize(Decimal("0.01"))),
        "currency": "USD",
        "calculation_method": "deterministic_decimal",
    }


def tool_get_upcoming_renewals(subscriptions: List[Dict[str, Any]], days_ahead: int = 14) -> Dict[str, Any]:
    """Finds subscriptions renewing within the next N days with exact renewal costs."""
    active = [s for s in subscriptions if s.get("status", "ACTIVE").upper() == "ACTIVE"]
    today = date.today()
    target_date = today + timedelta(days=days_ahead)

    renewing = []
    total_renewal_cost = Decimal("0.00")

    for s in active:
        ren_str = s.get("renewal_date")
        if ren_str:
            try:
                ren_dt = date.fromisoformat(str(ren_str)[:10])
                if today <= ren_dt <= target_date:
                    cost_dec = to_decimal(s.get("cost", 0))
                    total_renewal_cost += cost_dec
                    days_left = (ren_dt - today).days
                    renewing.append({
                        "id": s.get("id"),
                        "name": s.get("name"),
                        "cost": float(cost_dec),
                        "currency": s.get("currency", "USD"),
                        "billing_cycle": s.get("billing_cycle"),
                        "renewal_date": ren_dt.isoformat(),
                        "days_until_renewal": days_left,
                        "category": s.get("category", "General"),
                    })
            except Exception:
                pass

    renewing.sort(key=lambda x: x["days_until_renewal"])
    return {
        "tool_name": "get_upcoming_renewals",
        "days_window": days_ahead,
        "count": len(renewing),
        "total_renewal_amount": float(total_renewal_cost.quantize(Decimal("0.01"))),
        "renewals": renewing,
    }


def tool_get_category_breakdown(subscriptions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Groups expenditures by category with percentage share and total costs."""
    active = [s for s in subscriptions if s.get("status", "ACTIVE").upper() == "ACTIVE"]
    cat_spend: Dict[str, Decimal] = {}
    total = Decimal("0.00")

    for s in active:
        m = monthly_equiv(to_decimal(s.get("cost", 0)), str(s.get("billing_cycle", "MONTHLY")))
        cat = s.get("category") or s.get("category_name") or "General"
        cat_spend[cat] = cat_spend.get(cat, Decimal("0.00")) + m
        total += m

    results = []
    for cat, amount in cat_spend.items():
        pct = float(((amount / total) * Decimal("100")).quantize(Decimal("0.1"))) if total > 0 else 0.0
        results.append({
            "category": cat,
            "monthly_amount": float(amount.quantize(Decimal("0.01"))),
            "percentage": pct,
        })

    results.sort(key=lambda x: x["monthly_amount"], reverse=True)
    return {
        "tool_name": "get_category_breakdown",
        "categories": results,
        "total_monthly_spend": float(total.quantize(Decimal("0.01"))),
    }


def tool_identify_savings(subscriptions: List[Dict[str, Any]], max_utility: int = 5) -> Dict[str, Any]:
    """Identifies subscriptions with low utility ratings and non-essential classification for budget reduction."""
    active = [s for s in subscriptions if s.get("status", "ACTIVE").upper() == "ACTIVE"]
    candidates = []
    total_savings = Decimal("0.00")

    for s in active:
        util = int(s.get("utility_score", 5))
        is_ess = bool(s.get("is_essential", False))
        if util <= max_utility and not is_ess:
            m = monthly_equiv(to_decimal(s.get("cost", 0)), str(s.get("billing_cycle", "MONTHLY")))
            total_savings += m
            candidates.append({
                "id": s.get("id"),
                "name": s.get("name"),
                "cost": float(to_decimal(s.get("cost", 0))),
                "monthly_equivalent": float(m),
                "billing_cycle": s.get("billing_cycle"),
                "utility_score": util,
                "category": s.get("category") or s.get("category_name") or "General",
            })

    candidates.sort(key=lambda x: x["monthly_equivalent"], reverse=True)
    return {
        "tool_name": "identify_savings",
        "potential_monthly_savings": float(total_savings.quantize(Decimal("0.01"))),
        "potential_annual_savings": float((total_savings * Decimal("12")).quantize(Decimal("0.01"))),
        "low_utility_subscriptions": candidates,
    }


def tool_find_most_expensive(subscriptions: List[Dict[str, Any]], top_n: int = 5) -> Dict[str, Any]:
    """Ranks active subscriptions by their normalized monthly expense."""
    active = [s for s in subscriptions if s.get("status", "ACTIVE").upper() == "ACTIVE"]
    items = []
    for s in active:
        m = monthly_equiv(to_decimal(s.get("cost", 0)), str(s.get("billing_cycle", "MONTHLY")))
        items.append({
            "id": s.get("id"),
            "name": s.get("name"),
            "cost": float(to_decimal(s.get("cost", 0))),
            "monthly_equivalent": float(m),
            "billing_cycle": s.get("billing_cycle"),
            "category": s.get("category") or s.get("category_name") or "General",
        })

    items.sort(key=lambda x: x["monthly_equivalent"], reverse=True)
    return {
        "tool_name": "find_most_expensive",
        "most_expensive_subscriptions": items[:top_n],
    }
