from fastapi import status


def test_user_cannot_view_another_users_subscription(
    client, second_user_headers, sample_subscription
):
    # sample_subscription belongs to test_user. second_user requests it.
    response = client.get(
        f"/api/subscriptions/{sample_subscription.id}",
        headers=second_user_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_user_cannot_update_another_users_subscription(
    client, second_user_headers, sample_subscription
):
    update_data = {"name": "Hacked Subscription Name"}
    response = client.put(
        f"/api/subscriptions/{sample_subscription.id}",
        json=update_data,
        headers=second_user_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_user_cannot_delete_another_users_subscription(
    client, second_user_headers, sample_subscription
):
    response = client.delete(
        f"/api/subscriptions/{sample_subscription.id}",
        headers=second_user_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_analytics_isolated_per_user(
    client, auth_headers, second_user_headers, sample_subscription
):
    # test_user has sample_subscription ($22.99)
    res1 = client.get("/api/analytics/summary", headers=auth_headers)
    assert res1.json()["active_subscriptions_count"] >= 1
    assert res1.json()["total_monthly_spend"] >= 22.99

    # second_user has 0 subscriptions
    res2 = client.get("/api/analytics/summary", headers=second_user_headers)
    assert res2.json()["active_subscriptions_count"] == 0
    assert res2.json()["total_monthly_spend"] == 0.0


def test_rag_cannot_retrieve_another_users_subscription(flask_client):
    # Vector store isolation test
    from ai_service.rag.vector_store import vector_manager

    # Index User 1 subscriptions
    user1_subs = [
        {"id": 101, "name": "Confidential Enterprise SaaS", "cost": 500.0, "category": "Secret", "monthly_cost": 500.0}
    ]
    vector_manager.index_subscriptions(user_id=1, subscriptions=user1_subs)

    # User 2 performs search
    res = vector_manager.similarity_search(user_id=2, query="Enterprise SaaS")
    # Must be empty because user 2 has no documents
    assert len(res) == 0
