from typing import List, Optional, Dict, Any
from datetime import date, timedelta
from decimal import Decimal
import logging
import csv
import io
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.core.config import settings
from backend.app.models.subscription import Subscription, SubscriptionStatus, BillingCycle
from backend.app.models.category import Category
from backend.app.models.budget import Budget
from backend.app.models.expense import Expense
from backend.app.schemas.analytics import (
    ExpenseSummaryResponse,
    CategorySpendingItem,
    CategorySpendingResponse,
    MonthlySpendingTrendItem,
    TrendsResponse,
    BudgetUtilizationResponse,
    MostExpensiveItem,
)
from backend.app.core.cache import cache

logger = logging.getLogger(__name__)


class AnalyticsService:

    @staticmethod
    def _call_flask_analytics(endpoint: str, payload: dict) -> Optional[dict]:
        """Authenticated call to internal Flask Analytics Service with timeout and error handling."""
        url = f"{settings.ANALYTICS_SERVICE_URL}{endpoint}"
        headers = {"X-Internal-Secret": settings.INTERNAL_SERVICE_SECRET}
        try:
            with httpx.Client(timeout=0.2) as client:
                res = client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    return res.json()
        except Exception as e:
            logger.debug("Flask analytics service call to %s failed (%s); using in-process engine.", endpoint, e)
        return None

    @staticmethod
    def get_expense_summary(db: Session, user_id: int, use_cache: bool = True) -> ExpenseSummaryResponse:
        cache_key = f"user:{user_id}:analytics:summary"
        if use_cache:
            cached_data = cache.get(cache_key)
            if cached_data:
                cached_data["cached"] = True
                return ExpenseSummaryResponse(**cached_data)

        # Retrieve all user subscriptions
        subs = db.query(Subscription).filter(Subscription.user_id == user_id).all()
        active_subs = [s for s in subs if s.status == SubscriptionStatus.ACTIVE]

        # User budget
        budget_obj = db.query(Budget).filter(Budget.user_id == user_id).first()
        monthly_budget = float(budget_obj.monthly_limit) if budget_obj else 250.00

        # Try internal Flask analytics service first
        sub_payload = [
            {
                "id": s.id,
                "name": s.name,
                "cost": float(s.cost),
                "billing_cycle": s.billing_cycle.value if hasattr(s.billing_cycle, "value") else str(s.billing_cycle),
                "status": s.status.value if hasattr(s.status, "value") else str(s.status),
                "category_name": s.category.name if s.category else "General",
                "renewal_date": s.renewal_date.isoformat() if s.renewal_date else None,
                "utility_score": s.utility_score,
                "is_essential": s.is_essential,
            }
            for s in subs
        ]
        flask_res = AnalyticsService._call_flask_analytics("/analytics/aggregate", {
            "subscriptions": sub_payload,
            "monthly_budget": monthly_budget,
        })
        if flask_res:
            flask_res["cached"] = False
            cache.set(cache_key, flask_res, ttl=300)
            return ExpenseSummaryResponse(**flask_res)

        # Fallback local calculation
        total_monthly = sum(s.monthly_equivalent_cost for s in active_subs)
        total_annual = total_monthly * 12.0

        today = date.today()
        upcoming_7d = [
            s for s in active_subs
            if today <= s.renewal_date <= (today + timedelta(days=7))
        ]
        upcoming_30d = [
            s for s in active_subs
            if today <= s.renewal_date <= (today + timedelta(days=30))
        ]

        budget_utilization = (total_monthly / monthly_budget * 100.0) if monthly_budget > 0 else 0.0

        # Potential savings: non-essential subscriptions with utility score <= 4
        potential_savings = sum(
            s.monthly_equivalent_cost for s in active_subs
            if not s.is_essential and s.utility_score <= 4
        )

        # Most expensive subscription
        most_expensive = None
        if active_subs:
            sorted_subs = sorted(active_subs, key=lambda s: s.monthly_equivalent_cost, reverse=True)
            top = sorted_subs[0]
            cat_name = top.category.name if top.category else "General"
            cycle_str = top.billing_cycle.value if hasattr(top.billing_cycle, "value") else str(top.billing_cycle)
            most_expensive = MostExpensiveItem(
                id=top.id,
                name=top.name,
                cost=float(top.cost),
                billing_cycle=cycle_str,
                monthly_equivalent=round(top.monthly_equivalent_cost, 2),
                category_name=cat_name,
            )

        resp_dict = {
            "total_monthly_spend": round(total_monthly, 2),
            "total_annual_spend": round(total_annual, 2),
            "active_subscriptions_count": len(active_subs),
            "total_subscriptions_count": len(subs),
            "upcoming_renewals_7d_count": len(upcoming_7d),
            "upcoming_renewals_30d_count": len(upcoming_30d),
            "monthly_budget": round(monthly_budget, 2),
            "budget_utilization_pct": round(budget_utilization, 1),
            "potential_monthly_savings": round(potential_savings, 2),
            "most_expensive_subscription": most_expensive.model_dump() if most_expensive else None,
            "cached": False,
        }

        # Save to cache
        cache.set(cache_key, resp_dict, ttl=300)

        return ExpenseSummaryResponse(**resp_dict)

    @staticmethod
    def get_category_spending(db: Session, user_id: int, use_cache: bool = True) -> CategorySpendingResponse:
        cache_key = f"user:{user_id}:analytics:categories"
        if use_cache:
            cached_data = cache.get(cache_key)
            if cached_data:
                cached_data["cached"] = True
                return CategorySpendingResponse(**cached_data)

        active_subs = (
            db.query(Subscription)
            .filter(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE,
            )
            .all()
        )

        total_spend = sum(s.monthly_equivalent_cost for s in active_subs)

        cat_groups = {}
        for s in active_subs:
            cat = s.category
            cat_id = cat.id if cat else 0
            cat_name = cat.name if cat else "Uncategorized"
            cat_color = cat.color if cat else "#6b7280"
            cat_icon = cat.icon if cat else "category"

            if cat_id not in cat_groups:
                cat_groups[cat_id] = {
                    "category_id": cat_id,
                    "category_name": cat_name,
                    "total_monthly_spend": 0.0,
                    "count": 0,
                    "color": cat_color,
                    "icon": cat_icon,
                }
            cat_groups[cat_id]["total_monthly_spend"] += s.monthly_equivalent_cost
            cat_groups[cat_id]["count"] += 1

        items = []
        for cat_data in cat_groups.values():
            pct = (cat_data["total_monthly_spend"] / total_spend * 100.0) if total_spend > 0 else 0.0
            items.append(
                CategorySpendingItem(
                    category_id=cat_data["category_id"],
                    category_name=cat_data["category_name"],
                    total_monthly_spend=round(cat_data["total_monthly_spend"], 2),
                    count=cat_data["count"],
                    percentage=round(pct, 1),
                    color=cat_data["color"],
                    icon=cat_data["icon"],
                )
            )

        items.sort(key=lambda x: x.total_monthly_spend, reverse=True)

        resp_dict = {
            "items": [item.model_dump() for item in items],
            "total_monthly": round(total_spend, 2),
            "cached": False,
        }

        cache.set(cache_key, resp_dict, ttl=300)
        return CategorySpendingResponse(**resp_dict)

    @staticmethod
    def get_monthly_spending_trends(
        db: Session, user_id: int, months: int = 6, use_cache: bool = True
    ) -> TrendsResponse:
        cache_key = f"user:{user_id}:analytics:trends:{months}"
        if use_cache:
            cached_data = cache.get(cache_key)
            if cached_data:
                cached_data["cached"] = True
                return TrendsResponse(**cached_data)

        # Baseline: calculate active recurring monthly spend
        active_subs = (
            db.query(Subscription)
            .filter(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE,
            )
            .all()
        )
        base_monthly = sum(s.monthly_equivalent_cost for s in active_subs)
        sub_count = len(active_subs)

        today = date.today()
        trends = []
        for i in range(months - 1, -1, -1):
            # Compute past month dates
            year = today.year
            month = today.month - i
            while month <= 0:
                month += 12
                year -= 1

            month_label = f"{year}-{month:02d}"

            # Query historical recorded expenses in this month if available
            start_dt = date(year, month, 1)
            if month == 12:
                end_dt = date(year + 1, 1, 1)
            else:
                end_dt = date(year, month + 1, 1)

            expenses_sum = (
                db.query(func.sum(Expense.amount))
                .filter(
                    Expense.user_id == user_id,
                    Expense.expense_date >= start_dt,
                    Expense.expense_date < end_dt,
                )
                .scalar()
            )

            # If logged expenses exist, use them; otherwise, project the recurring subscription baseline
            month_spend = float(expenses_sum) if expenses_sum is not None else base_monthly

            trends.append(
                MonthlySpendingTrendItem(
                    month_label=month_label,
                    year=year,
                    month=month,
                    total_spend=round(month_spend, 2),
                    active_subscriptions_count=sub_count,
                )
            )

        resp_dict = {
            "trends": [t.model_dump() for t in trends],
            "cached": False,
        }

        cache.set(cache_key, resp_dict, ttl=300)
        return TrendsResponse(**resp_dict)

    @staticmethod
    def get_budget_utilization(db: Session, user_id: int) -> BudgetUtilizationResponse:
        budget_obj = db.query(Budget).filter(Budget.user_id == user_id).first()
        monthly_budget = float(budget_obj.monthly_limit) if budget_obj else 250.00

        active_subs = (
            db.query(Subscription)
            .filter(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE,
            )
            .all()
        )
        current_spend = sum(s.monthly_equivalent_cost for s in active_subs)
        remaining = max(0.0, monthly_budget - current_spend)
        pct = (current_spend / monthly_budget * 100.0) if monthly_budget > 0 else 0.0
        is_over = current_spend > monthly_budget

        if is_over:
            status_label = "OVER_BUDGET"
        elif pct >= 80:
            status_label = "WARNING"
        else:
            status_label = "HEALTHY"

        return BudgetUtilizationResponse(
            monthly_budget=round(monthly_budget, 2),
            current_monthly_spend=round(current_spend, 2),
            remaining_budget=round(remaining, 2),
            utilization_percentage=round(pct, 1),
            is_over_budget=is_over,
            status_label=status_label,
        )

    @staticmethod
    def get_comprehensive_report(db: Session, user_id: int) -> Dict[str, Any]:
        """Aggregate summary, category breakdown, trends, budget, and redundancy detection."""
        summary = AnalyticsService.get_expense_summary(db=db, user_id=user_id, use_cache=False)
        categories = AnalyticsService.get_category_spending(db=db, user_id=user_id, use_cache=False)
        trends = AnalyticsService.get_monthly_spending_trends(db=db, user_id=user_id, months=6, use_cache=False)
        budget = AnalyticsService.get_budget_utilization(db=db, user_id=user_id)

        # Retrieve user subs to detect redundancies
        subs = db.query(Subscription).filter(Subscription.user_id == user_id).all()
        sub_payload = [
            {
                "id": s.id,
                "name": s.name,
                "cost": float(s.cost),
                "billing_cycle": s.billing_cycle.value if hasattr(s.billing_cycle, "value") else str(s.billing_cycle),
                "status": s.status.value if hasattr(s.status, "value") else str(s.status),
                "category_name": s.category.name if s.category else "General",
                "renewal_date": s.renewal_date.isoformat() if s.renewal_date else None,
                "utility_score": s.utility_score,
                "is_essential": s.is_essential,
            }
            for s in subs
        ]
        redundancies = AnalyticsService._call_flask_analytics("/analytics/redundancy", {"subscriptions": sub_payload})
        if not redundancies:
            # Local redundancy detection fallback
            active = [s for s in subs if s.status == SubscriptionStatus.ACTIVE]
            low_util = [
                {
                    "id": s.id,
                    "name": s.name,
                    "monthly_cost": round(s.monthly_equivalent_cost, 2),
                    "utility_score": s.utility_score,
                    "category": s.category.name if s.category else "General",
                    "recommendation": "Review for cancellation due to low utilization rating.",
                }
                for s in active if s.utility_score <= 4 and not s.is_essential
            ]
            redundancies = {
                "category_redundancies": [],
                "low_utility_subscriptions": low_util,
                "total_potential_savings": round(sum(it["monthly_cost"] for it in low_util), 2),
            }

        return {
            "summary": summary.model_dump(),
            "category_breakdown": categories.model_dump().get("items", []),
            "spending_trends": trends.model_dump().get("trends", []),
            "budget": budget.model_dump(),
            "redundancies": redundancies,
            "generated_at": date.today().isoformat(),
        }

    @staticmethod
    def export_subscriptions_csv(db: Session, user_id: int) -> str:
        """Generate CSV string of user subscriptions with financial calculations."""
        subs = db.query(Subscription).filter(Subscription.user_id == user_id).all()
        output = io.StringIO()
        writer = csv.writer(output)
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
            "Payment Method",
        ])
        for s in subs:
            cycle = s.billing_cycle.value if hasattr(s.billing_cycle, "value") else str(s.billing_cycle)
            status_str = s.status.value if hasattr(s.status, "value") else str(s.status)
            writer.writerow([
                s.id,
                s.name,
                s.category.name if s.category else "General",
                cycle,
                f"{float(s.cost):.2f}",
                s.currency,
                f"{s.monthly_equivalent_cost:.2f}",
                f"{s.annual_equivalent_cost:.2f}",
                s.renewal_date.isoformat() if s.renewal_date else "",
                status_str,
                s.utility_score,
                "YES" if s.is_essential else "NO",
                s.payment_method or "N/A",
            ])
        return output.getvalue()
