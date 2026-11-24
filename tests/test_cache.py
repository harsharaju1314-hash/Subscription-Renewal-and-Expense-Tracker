import time
from backend.app.core.cache import cache


def test_cache_set_and_get():
    key = "test:unit:key1"
    val = {"foo": "bar", "number": 42}
    cache.set(key, val, ttl=60)
    retrieved = cache.get(key)
    assert retrieved == val


def test_cache_delete():
    key = "test:unit:key2"
    cache.set(key, {"temp": True}, ttl=60)
    assert cache.get(key) is not None
    cache.delete(key)
    assert cache.get(key) is None


def test_cache_expiration():
    key = "test:unit:expiring"
    cache.set(key, {"expired": False}, ttl=1)
    assert cache.get(key) is not None
    time.sleep(1.2)
    assert cache.get(key) is None


def test_cache_invalidation_on_subscription_create(client, auth_headers, test_user, db_session):
    from backend.app.models.category import Category
    from datetime import date, timedelta
    cat = db_session.query(Category).first()

    # Pre-populate cache by requesting summary
    res1 = client.get("/api/analytics/summary", headers=auth_headers)
    assert res1.status_code == 200
    cache_key = f"user:{test_user.id}:analytics:summary"
    assert cache.get(cache_key) is not None

    # Creating a new subscription must invalidate user cache
    payload = {
        "name": "AWS Dev",
        "category_id": cat.id,
        "cost": 50.00,
        "currency": "USD",
        "billing_cycle": "MONTHLY",
        "start_date": date.today().isoformat(),
        "renewal_date": (date.today() + timedelta(days=20)).isoformat(),
        "status": "ACTIVE",
        "auto_renew": True,
        "utility_score": 9,
        "is_essential": True,
    }
    client.post("/api/subscriptions", json=payload, headers=auth_headers)

    # Cached summary should now be invalidated
    assert cache.get(cache_key) is None


def test_cache_invalidation_on_subscription_delete(client, auth_headers, test_user, sample_subscription):
    cache_key = f"user:{test_user.id}:analytics:summary"
    client.get("/api/analytics/summary", headers=auth_headers)
    assert cache.get(cache_key) is not None

    client.delete(f"/api/subscriptions/{sample_subscription.id}", headers=auth_headers)
    assert cache.get(cache_key) is None
