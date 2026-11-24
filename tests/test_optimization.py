from decimal import Decimal
from datetime import date, timedelta
from backend.app.models.subscription import Subscription, BillingCycle, SubscriptionStatus
from backend.app.models.category import Category


def test_optimization_within_budget(client, auth_headers, test_user, db_session):
    cat = db_session.query(Category).first()
    # Add a small subscription
    sub = Subscription(
        user_id=test_user.id,
        category_id=cat.id,
        name="Cheap Service",
        cost=Decimal("15.00"),
        billing_cycle=BillingCycle.MONTHLY,
        start_date=date.today(),
        renewal_date=date.today() + timedelta(days=20),
        status=SubscriptionStatus.ACTIVE,
        utility_score=7,
        is_essential=False,
    )
    db_session.add(sub)
    db_session.commit()

    # Target budget is $100 (more than enough for $15)
    payload = {"target_monthly_budget": 100.0}
    response = client.post("/api/optimization/solve", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_budget_met"] is True
    assert data["total_monthly_savings"] == 0.0
    assert len(data["retained_subscriptions"]) >= 1


def test_optimization_exceeding_budget_cancels_low_utility(client, auth_headers, test_user, db_session):
    cat = db_session.query(Category).first()

    # Create 3 subscriptions:
    # 1. High utility: $30, utility 9
    # 2. Med utility: $30, utility 6
    # 3. Low utility: $30, utility 2
    for name, cost, util in [("SubHigh", 30, 9), ("SubMed", 30, 6), ("SubLow", 30, 2)]:
        s = Subscription(
            user_id=test_user.id,
            category_id=cat.id,
            name=name,
            cost=Decimal(str(cost)),
            billing_cycle=BillingCycle.MONTHLY,
            start_date=date.today(),
            renewal_date=date.today() + timedelta(days=10),
            status=SubscriptionStatus.ACTIVE,
            utility_score=util,
            is_essential=False,
        )
        db_session.add(s)
    db_session.commit()

    # Target budget: $50 (can only afford one $30 sub plus maybe small change, or two if sum <= 50)
    payload = {"target_monthly_budget": 50.0}
    response = client.post("/api/optimization/solve", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    cancelled_names = [it["name"] for it in data["cancelled_subscriptions"]]
    retained_names = [it["name"] for it in data["retained_subscriptions"]]

    # SubLow must be recommended for cancellation
    assert "SubLow" in cancelled_names
    assert data["total_monthly_savings"] > 0
    assert data["optimized_monthly_spend"] <= 50.0


def test_optimization_essential_subscriptions_always_retained(client, auth_headers, test_user, db_session):
    cat = db_session.query(Category).first()
    # Essential subscription
    sub_ess = Subscription(
        user_id=test_user.id,
        category_id=cat.id,
        name="Essential Internet",
        cost=Decimal("70.00"),
        billing_cycle=BillingCycle.MONTHLY,
        start_date=date.today(),
        renewal_date=date.today() + timedelta(days=5),
        status=SubscriptionStatus.ACTIVE,
        utility_score=10,
        is_essential=True,
    )
    # Optional subscription
    sub_opt = Subscription(
        user_id=test_user.id,
        category_id=cat.id,
        name="Optional Gaming",
        cost=Decimal("20.00"),
        billing_cycle=BillingCycle.MONTHLY,
        start_date=date.today(),
        renewal_date=date.today() + timedelta(days=5),
        status=SubscriptionStatus.ACTIVE,
        utility_score=4,
        is_essential=False,
    )
    db_session.add_all([sub_ess, sub_opt])
    db_session.commit()

    # Budget is $75 (enough for Essential, not enough for both)
    payload = {"target_monthly_budget": 75.0}
    response = client.post("/api/optimization/solve", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    retained_ids = [it["id"] for it in data["retained_subscriptions"]]
    cancelled_ids = [it["id"] for it in data["cancelled_subscriptions"]]

    assert sub_ess.id in retained_ids
    assert sub_opt.id in cancelled_ids


def test_optimization_essential_exceeds_budget(client, auth_headers, test_user, db_session):
    cat = db_session.query(Category).first()
    sub_ess = Subscription(
        user_id=test_user.id,
        category_id=cat.id,
        name="Super Critical Enterprise Tool",
        cost=Decimal("300.00"),
        billing_cycle=BillingCycle.MONTHLY,
        start_date=date.today(),
        renewal_date=date.today() + timedelta(days=5),
        status=SubscriptionStatus.ACTIVE,
        utility_score=10,
        is_essential=True,
    )
    db_session.add(sub_ess)
    db_session.commit()

    payload = {"target_monthly_budget": 100.0}
    response = client.post("/api/optimization/solve", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["optimization_status"] == "budget_deficit"
    assert data["essential_spend_total"] >= 300.0


def test_optimization_custom_utility_overrides(client, auth_headers, test_user, sample_subscription):
    # Override sample_subscription utility to 1
    payload = {
        "target_monthly_budget": 10.0,
        "custom_utility_overrides": {sample_subscription.id: 1},
        "custom_essential_overrides": {sample_subscription.id: False},
    }
    response = client.post("/api/optimization/solve", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert sample_subscription.id in [c["id"] for c in data["cancelled_subscriptions"]]


def test_optimization_empty_subscriptions(client, second_user_headers):
    # second_user has no subscriptions
    payload = {"target_monthly_budget": 150.0}
    response = client.post("/api/optimization/solve", json=payload, headers=second_user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["baseline_monthly_spend"] == 0.0
    assert data["retained_subscriptions"] == []
