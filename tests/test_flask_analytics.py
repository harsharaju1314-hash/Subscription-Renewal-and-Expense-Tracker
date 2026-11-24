"""
Tests for Internal Flask Analytics Microservice
Validates:
  - Inter-service authentication with X-Internal-Secret
  - Deterministic Decimal-precision financial aggregation
  - Category spending breakdown
  - Redundant subscription detection
  - CSV export generation
"""
import pytest
from analytics_service.app.main import create_app
from analytics_service.app.config import settings


@pytest.fixture
def flask_test_client():
    settings.ENVIRONMENT = "production"  # enforce token validation
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def internal_headers():
    return {"X-Internal-Secret": settings.INTERNAL_SERVICE_SECRET}


@pytest.fixture
def sample_subscriptions():
    return [
        {
            "id": 1,
            "name": "Netflix Premium",
            "cost": 19.99,
            "billing_cycle": "monthly",
            "category_id": 1,
            "category_name": "Entertainment",
            "status": "active",
            "utility_score": 8,
            "is_essential": False,
        },
        {
            "id": 2,
            "name": "AWS Cloud Hosting",
            "cost": 120.00,
            "billing_cycle": "quarterly",
            "category_id": 2,
            "category_name": "Cloud & Hosting",
            "status": "active",
            "utility_score": 9,
            "is_essential": True,
        },
        {
            "id": 3,
            "name": "Unused Magazine",
            "cost": 10.00,
            "billing_cycle": "monthly",
            "category_id": 1,
            "category_name": "Entertainment",
            "status": "active",
            "utility_score": 2,
            "is_essential": False,
        },
    ]


def test_flask_health_endpoint(flask_test_client):
    res = flask_test_client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert "Analytics" in data["service"]


def test_flask_unauthorized_without_secret(flask_test_client):
    res = flask_test_client.post("/analytics/aggregate", json={"subscriptions": []})
    assert res.status_code == 401
    assert "Unauthorized" in res.get_json()["error"]


def test_flask_aggregate_summary(flask_test_client, internal_headers, sample_subscriptions):
    payload = {
        "subscriptions": sample_subscriptions,
        "monthly_budget": 150.00,
    }
    res = flask_test_client.post("/analytics/aggregate", json=payload, headers=internal_headers)
    assert res.status_code == 200
    data = res.get_json()
    assert "total_monthly_spend" in data
    assert "total_annual_spend" in data
    assert "budget_utilization_pct" in data
    assert data["active_subscriptions_count"] == 3
    # Netflix ($19.99) + AWS ($40/mo) + Unused ($10) = $69.99
    assert data["total_monthly_spend"] == 69.99


def test_flask_category_breakdown(flask_test_client, internal_headers, sample_subscriptions):
    payload = {"subscriptions": sample_subscriptions}
    res = flask_test_client.post("/analytics/breakdown", json=payload, headers=internal_headers)
    assert res.status_code == 200
    data = res.get_json()
    assert "categories" in data
    assert len(data["categories"]) == 2
    cat_names = [it["category_name"] for it in data["categories"]]
    assert "Entertainment" in cat_names
    assert "Cloud & Hosting" in cat_names


def test_flask_redundancy_detection(flask_test_client, internal_headers, sample_subscriptions):
    payload = {"subscriptions": sample_subscriptions}
    res = flask_test_client.post("/analytics/redundancy", json=payload, headers=internal_headers)
    assert res.status_code == 200
    data = res.get_json()
    assert "low_utility_subscriptions" in data
    # "Unused Magazine" has utility score 2 <= 4
    low_util = data["low_utility_subscriptions"]
    assert any(item["name"] == "Unused Magazine" for item in low_util)


def test_flask_export_csv(flask_test_client, internal_headers, sample_subscriptions):
    payload = {"subscriptions": sample_subscriptions}
    res = flask_test_client.post("/analytics/export-csv", json=payload, headers=internal_headers)
    assert res.status_code == 200
    assert "text/csv" in res.content_type
    csv_text = res.get_data(as_text=True)
    assert "Subscription ID,Name,Category" in csv_text
    assert "Netflix Premium" in csv_text
