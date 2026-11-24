from decimal import Decimal
from datetime import date
from backend.app.models.subscription import Subscription, BillingCycle, SubscriptionStatus


def test_monthly_equivalent_monthly_cycle():
    sub = Subscription(
        cost=Decimal("20.00"),
        billing_cycle=BillingCycle.MONTHLY,
    )
    assert sub.monthly_equivalent_cost == 20.0


def test_monthly_equivalent_annual_cycle():
    sub = Subscription(
        cost=Decimal("120.00"),
        billing_cycle=BillingCycle.ANNUAL,
    )
    assert sub.monthly_equivalent_cost == 10.0


def test_monthly_equivalent_quarterly_cycle():
    sub = Subscription(
        cost=Decimal("60.00"),
        billing_cycle=BillingCycle.QUARTERLY,
    )
    assert sub.monthly_equivalent_cost == 20.0


def test_monthly_equivalent_weekly_cycle():
    sub = Subscription(
        cost=Decimal("10.00"),
        billing_cycle=BillingCycle.WEEKLY,
    )
    # (10 * 52) / 12 = 43.333333333333336
    assert round(sub.monthly_equivalent_cost, 2) == 43.33


def test_annual_equivalent_cost():
    sub = Subscription(
        cost=Decimal("15.00"),
        billing_cycle=BillingCycle.MONTHLY,
    )
    assert sub.annual_equivalent_cost == 180.0


def test_analytics_summary_totals(client, auth_headers, sample_subscription):
    response = client.get("/api/analytics/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_monthly_spend"] >= 22.99
    assert data["total_annual_spend"] >= 22.99 * 12
    assert data["active_subscriptions_count"] >= 1
    assert data["monthly_budget"] == 200.0
