from datetime import date, timedelta


def test_flask_health_endpoint(flask_client):
    response = flask_client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "Financial AI" in data["service"]


def test_flask_ai_chat_spending_query(flask_client):
    payload = {
        "user_id": 99,
        "query": "How much am I spending every month?",
        "subscriptions": [
            {
                "id": 1,
                "name": "Netflix Premium",
                "cost": 22.99,
                "billing_cycle": "MONTHLY",
                "monthly_cost": 22.99,
                "category": "Streaming",
                "renewal_date": (date.today() + timedelta(days=5)).isoformat(),
                "is_essential": False,
                "utility_score": 8,
            },
            {
                "id": 2,
                "name": "Spotify Premium",
                "cost": 10.99,
                "billing_cycle": "MONTHLY",
                "monthly_cost": 10.99,
                "category": "Music",
                "renewal_date": (date.today() + timedelta(days=20)).isoformat(),
                "is_essential": True,
                "utility_score": 9,
            }
        ]
    }
    response = flask_client.post("/ai/chat", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "answer" in data
    assert "33.98" in data["answer"]  # 22.99 + 10.99
    assert len(data["sources"]) > 0


def test_flask_ai_chat_most_expensive_query(flask_client):
    payload = {
        "user_id": 99,
        "query": "Which subscriptions cost me the most?",
        "subscriptions": [
            {
                "id": 10,
                "name": "Cloud Cluster",
                "cost": 150.00,
                "billing_cycle": "MONTHLY",
                "monthly_cost": 150.00,
                "category": "Cloud",
                "renewal_date": date.today().isoformat(),
                "is_essential": True,
                "utility_score": 10,
            },
            {
                "id": 11,
                "name": "Gym Pass",
                "cost": 30.00,
                "billing_cycle": "MONTHLY",
                "monthly_cost": 30.00,
                "category": "Fitness",
                "renewal_date": date.today().isoformat(),
                "is_essential": False,
                "utility_score": 6,
            }
        ]
    }
    response = flask_client.post("/ai/chat", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "Cloud Cluster" in data["answer"]
    assert any(s["name"] == "Cloud Cluster" for s in data["sources"])


def test_flask_ai_chat_renewals_query(flask_client):
    ren_date = (date.today() + timedelta(days=4)).isoformat()
    payload = {
        "user_id": 99,
        "query": "What subscriptions renew next week?",
        "subscriptions": [
            {
                "id": 20,
                "name": "GitHub Copilot",
                "cost": 10.00,
                "billing_cycle": "MONTHLY",
                "monthly_cost": 10.00,
                "category": "Developer Tools",
                "renewal_date": ren_date,
                "is_essential": True,
                "utility_score": 10,
            }
        ]
    }
    response = flask_client.post("/ai/chat", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "GitHub Copilot" in data["answer"]
    assert ren_date in data["answer"]


def test_flask_ai_chat_savings_query(flask_client):
    payload = {
        "user_id": 99,
        "query": "How can I reduce my monthly expenses?",
        "subscriptions": [
            {
                "id": 30,
                "name": "Unused Magazine",
                "cost": 8.00,
                "billing_cycle": "MONTHLY",
                "monthly_cost": 8.00,
                "category": "News",
                "renewal_date": date.today().isoformat(),
                "is_essential": False,
                "utility_score": 3,
            }
        ]
    }
    response = flask_client.post("/ai/chat", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "Unused Magazine" in data["answer"]
    assert "save" in data["answer"].lower()


def test_flask_ai_reindex_endpoint(flask_client):
    payload = {
        "user_id": 777,
        "subscriptions": [
            {
                "id": 1001,
                "name": "Audible Plus",
                "cost": 14.95,
                "billing_cycle": "MONTHLY",
                "monthly_cost": 14.95,
                "category": "Audio",
                "renewal_date": date.today().isoformat(),
            }
        ]
    }
    response = flask_client.post("/ai/reindex", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["indexed_documents_count"] == 1
