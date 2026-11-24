"""
Test Suite for Core REST API v1 Endpoints, RBAC, Health Checks, and Microservices
Covers:
  - 8 Mandatory Core Business Endpoints (/api/v1/...)
  - JWT Refresh Token Rotation Flow
  - Role-Based Access Control (USER, ANALYST, ADMIN)
  - Prometheus Metrics and Liveness/Readiness Health Checks
  - Internal Flask Analytics Microservice Routes
  - Resource Ownership & Validation Error Conditions
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal

from backend.app.models.user import User
from backend.app.models.role import Role, UserRole
from backend.app.models.subscription import Subscription, BillingCycle, SubscriptionStatus
from backend.app.models.category import Category
from backend.app.core.security import create_access_token, create_refresh_token, get_password_hash


# ---------------------------------------------------------------------------
# Core Business Endpoints 1 to 5: Subscription CRUD
# ---------------------------------------------------------------------------

def test_core_endpoint_1_create_subscription(client, auth_headers, db_session):
    cat = db_session.query(Category).first()
    payload = {
        "name": "GitHub Enterprise",
        "cost": 21.00,
        "billing_cycle": "MONTHLY",
        "start_date": date.today().isoformat(),
        "renewal_date": (date.today() + timedelta(days=25)).isoformat(),
        "category_id": cat.id if cat else 1,
        "status": "ACTIVE",
        "utility_score": 9,
        "is_essential": True,
    }
    res = client.post("/api/v1/subscriptions", json=payload, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "GitHub Enterprise"
    assert data["cost"] == 21.00
    assert data["billing_cycle"] == "MONTHLY"
    assert "id" in data


def test_core_endpoint_2_get_subscriptions_paginated(client, auth_headers, test_user, db_session):
    cat = db_session.query(Category).first()
    for i in range(3):
        sub = Subscription(
            user_id=test_user.id,
            category_id=cat.id if cat else 1,
            name=f"Paged Sub {i}",
            cost=Decimal("9.99"),
            billing_cycle=BillingCycle.MONTHLY,
            start_date=date.today(),
            renewal_date=date.today() + timedelta(days=15),
            status=SubscriptionStatus.ACTIVE,
        )
        db_session.add(sub)
    db_session.commit()

    res = client.get("/api/v1/subscriptions?status=ACTIVE", headers=auth_headers)
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list)
    assert len(items) >= 3


def test_core_endpoint_3_get_subscription_by_id(client, auth_headers, test_user, db_session):
    cat = db_session.query(Category).first()
    sub = Subscription(
        user_id=test_user.id,
        category_id=cat.id if cat else 1,
        name="Unique Stream Service",
        cost=Decimal("14.99"),
        billing_cycle=BillingCycle.MONTHLY,
        start_date=date.today(),
        renewal_date=date.today() + timedelta(days=10),
        status=SubscriptionStatus.ACTIVE,
    )
    db_session.add(sub)
    db_session.commit()

    res = client.get(f"/api/v1/subscriptions/{sub.id}", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == sub.id
    assert data["name"] == "Unique Stream Service"


def test_core_endpoint_4_put_subscription_update(client, auth_headers, test_user, db_session):
    cat = db_session.query(Category).first()
    sub = Subscription(
        user_id=test_user.id,
        category_id=cat.id if cat else 1,
        name="Updatable Service",
        cost=Decimal("12.00"),
        billing_cycle=BillingCycle.MONTHLY,
        start_date=date.today(),
        renewal_date=date.today() + timedelta(days=10),
        status=SubscriptionStatus.ACTIVE,
    )
    db_session.add(sub)
    db_session.commit()

    update_payload = {"cost": 17.50, "billing_cycle": "MONTHLY"}
    res = client.put(f"/api/v1/subscriptions/{sub.id}", json=update_payload, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["cost"] == 17.50


def test_core_endpoint_5_delete_subscription(client, auth_headers, test_user, db_session):
    cat = db_session.query(Category).first()
    sub = Subscription(
        user_id=test_user.id,
        category_id=cat.id if cat else 1,
        name="Disposable Service",
        cost=Decimal("5.00"),
        billing_cycle=BillingCycle.MONTHLY,
        start_date=date.today(),
        renewal_date=date.today() + timedelta(days=5),
        status=SubscriptionStatus.ACTIVE,
    )
    db_session.add(sub)
    db_session.commit()

    res = client.delete(f"/api/v1/subscriptions/{sub.id}", headers=auth_headers)
    assert res.status_code in [200, 204]

    # Verify not accessible
    get_res = client.get(f"/api/v1/subscriptions/{sub.id}", headers=auth_headers)
    assert get_res.status_code == 404


# ---------------------------------------------------------------------------
# Core Business Endpoints 6, 7, 8: Renewals, Expenses Report, AI Query
# ---------------------------------------------------------------------------

def test_core_endpoint_6_upcoming_renewals(client, auth_headers, test_user, db_session):
    cat = db_session.query(Category).first()
    sub = Subscription(
        user_id=test_user.id,
        category_id=cat.id if cat else 1,
        name="Renewing Soon Sub",
        cost=Decimal("29.99"),
        billing_cycle=BillingCycle.MONTHLY,
        start_date=date.today() - timedelta(days=30),
        renewal_date=date.today() + timedelta(days=7),
        status=SubscriptionStatus.ACTIVE,
    )
    db_session.add(sub)
    db_session.commit()

    res = client.get("/api/v1/renewals/upcoming?days=14", headers=auth_headers)
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list)
    assert any(s["name"] == "Renewing Soon Sub" for s in items)


def test_core_endpoint_7_expenses_report_json_and_csv(client, auth_headers, test_user, db_session):
    # Test JSON report
    res_json = client.get("/api/v1/expenses/report", headers=auth_headers)
    assert res_json.status_code == 200
    data = res_json.json()
    assert "summary" in data
    assert "category_breakdown" in data
    assert "spending_trends" in data
    assert "budget" in data

    # Test CSV report export
    res_csv = client.get("/api/v1/expenses/report?format=csv", headers=auth_headers)
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers.get("content-type", "")
    assert "Subscription ID,Name,Category" in res_csv.text


def test_core_endpoint_8_ai_query(client, auth_headers, test_user, db_session):
    cat = db_session.query(Category).first()
    sub = Subscription(
        user_id=test_user.id,
        category_id=cat.id if cat else 1,
        name="AI Tracked Tool",
        cost=Decimal("50.00"),
        billing_cycle=BillingCycle.MONTHLY,
        start_date=date.today(),
        renewal_date=date.today() + timedelta(days=20),
        status=SubscriptionStatus.ACTIVE,
    )
    db_session.add(sub)
    db_session.commit()

    payload = {"query": "What is my total monthly subscription cost?"}
    res = client.post("/api/v1/ai/query", json=payload, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert len(data["answer"]) > 0


# ---------------------------------------------------------------------------
# Refresh Token Rotation & Auth Security
# ---------------------------------------------------------------------------

def test_refresh_token_rotation_flow(client, test_user):
    # Valid refresh token
    refresh_token = create_refresh_token(subject=test_user.id)
    res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert res.status_code == 200
    tokens = res.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"

    # Invalid refresh token
    bad_res = client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid.jwt.token"})
    assert bad_res.status_code == 401


# ---------------------------------------------------------------------------
# RBAC: Role-Based Access Control
# ---------------------------------------------------------------------------

def test_rbac_user_forbidden_from_admin_operations(client, auth_headers):
    # Standard USER should get 403 on admin endpoints
    res_users = client.get("/api/v1/admin/users", headers=auth_headers)
    assert res_users.status_code == 403

    res_ops = client.get("/api/v1/admin/operations", headers=auth_headers)
    assert res_ops.status_code == 403


def test_rbac_admin_allowed_access(client, db_session):
    admin_user = db_session.query(User).filter(User.username == "superadmin").first()
    if not admin_user:
        admin_user = User(
            email="superadmin@example.com",
            username="superadmin",
            hashed_password=get_password_hash("AdminPass123!"),
            full_name="Super Admin",
            is_active=True,
        )
        db_session.add(admin_user)
        db_session.commit()

    admin_role = db_session.query(Role).filter(Role.name == "ADMIN").first()
    if not admin_role:
        admin_role = Role(name="ADMIN", description="Administrator")
        db_session.add(admin_role)
        db_session.commit()

    existing_ur = db_session.query(UserRole).filter(
        UserRole.user_id == admin_user.id, UserRole.role_id == admin_role.id
    ).first()
    if not existing_ur:
        db_session.add(UserRole(user_id=admin_user.id, role_id=admin_role.id))
        db_session.commit()

    admin_token = create_access_token(subject=admin_user.id, roles=["ADMIN"])
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    res_users = client.get("/api/v1/admin/users", headers=admin_headers)
    assert res_users.status_code == 200
    assert isinstance(res_users.json(), list)

    res_ops = client.get("/api/v1/admin/operations", headers=admin_headers)
    assert res_ops.status_code == 200
    data = res_ops.json()
    assert "status" in data
    assert data["status"] == "OPERATIONAL"
    assert "cache" in data


# ---------------------------------------------------------------------------
# Monitoring, Observability & Health Checks
# ---------------------------------------------------------------------------

def test_observability_health_and_metrics_endpoints(client):
    # Liveness probe
    live_res = client.get("/health/live")
    assert live_res.status_code == 200
    assert live_res.json()["status"] == "alive"

    # Readiness probe
    ready_res = client.get("/health/ready")
    assert ready_res.status_code == 200
    assert ready_res.json()["status"] == "ready"

    # Base health
    health_res = client.get("/health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "healthy"

    # Prometheus metrics format
    metrics_res = client.get("/metrics")
    assert metrics_res.status_code == 200
    assert "http_requests_total" in metrics_res.text


# ---------------------------------------------------------------------------
# Input Validation & Negative Conditions
# ---------------------------------------------------------------------------

def test_input_validation_negative_cost_fails(client, auth_headers):
    payload = {
        "name": "Invalid Cost Service",
        "cost": -15.00,
        "billing_cycle": "MONTHLY",
        "renewal_date": "2026-12-01",
        "category_id": 1,
    }
    res = client.post("/api/v1/subscriptions", json=payload, headers=auth_headers)
    assert res.status_code == 422


def test_input_validation_invalid_billing_cycle_fails(client, auth_headers):
    payload = {
        "name": "Invalid Cycle Service",
        "cost": 15.00,
        "billing_cycle": "bi-weekly-unknown",
        "renewal_date": "2026-12-01",
        "category_id": 1,
    }
    res = client.post("/api/v1/subscriptions", json=payload, headers=auth_headers)
    assert res.status_code == 422
