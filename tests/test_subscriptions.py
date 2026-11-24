from datetime import date, timedelta
from fastapi import status


def test_create_subscription_success(client, auth_headers, db_session):
    from backend.app.models.category import Category
    cat = db_session.query(Category).first()
    ren_date = (date.today() + timedelta(days=15)).isoformat()

    payload = {
        "name": "Spotify Premium",
        "category_id": cat.id,
        "cost": 10.99,
        "currency": "USD",
        "billing_cycle": "MONTHLY",
        "start_date": date.today().isoformat(),
        "renewal_date": ren_date,
        "status": "ACTIVE",
        "auto_renew": True,
        "utility_score": 9,
        "is_essential": True,
        "description": "Family music plan",
    }
    response = client.post("/api/subscriptions", json=payload, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Spotify Premium"
    assert data["monthly_equivalent_cost"] == 10.99
    assert data["is_essential"] is True


def test_get_subscriptions_list(client, auth_headers, sample_subscription):
    response = client.get("/api/subscriptions", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert any(s["id"] == sample_subscription.id for s in data)


def test_get_subscription_by_id(client, auth_headers, sample_subscription):
    response = client.get(f"/api/subscriptions/{sample_subscription.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == sample_subscription.id
    assert data["name"] == sample_subscription.name


def test_update_subscription(client, auth_headers, sample_subscription):
    update_payload = {
        "cost": 24.99,
        "utility_score": 10,
        "is_essential": True,
    }
    response = client.put(
        f"/api/subscriptions/{sample_subscription.id}",
        json=update_payload,
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["cost"] == 24.99
    assert data["utility_score"] == 10
    assert data["is_essential"] is True


def test_delete_subscription(client, auth_headers, sample_subscription):
    response = client.delete(
        f"/api/subscriptions/{sample_subscription.id}",
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify not found afterwards
    get_res = client.get(f"/api/subscriptions/{sample_subscription.id}", headers=auth_headers)
    assert get_res.status_code == status.HTTP_404_NOT_FOUND


def test_subscription_filter_by_status(client, auth_headers, sample_subscription):
    response = client.get("/api/subscriptions?status=ACTIVE", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(s["status"] == "ACTIVE" for s in data)


def test_subscription_filter_by_category(client, auth_headers, sample_subscription):
    cat_id = sample_subscription.category_id
    response = client.get(f"/api/subscriptions?category_id={cat_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(s["category_id"] == cat_id for s in data)


def test_upcoming_renewals_endpoint(client, auth_headers, sample_subscription):
    response = client.get("/api/subscriptions/renewals?days=30", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(item["id"] == sample_subscription.id for item in data)
