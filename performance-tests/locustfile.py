"""
Locust Load Testing Suite
Simulates 200+ concurrent users against FastAPI core business endpoints.
Measures:
  - Throughput (RPS)
  - P50, P95, P99 Latencies
  - Error rate (< 0.1% target for 99.9% availability)
"""
import random
from locust import HttpUser, task, between, events


class SubscriptionUser(HttpUser):
    wait_time = between(0.1, 0.5)
    token = None
    created_sub_ids = []

    def on_start(self):
        """Register or login to obtain a JWT bearer token."""
        random_suffix = random.randint(1000, 999999)
        email = f"loadtest_user_{random_suffix}@example.com"
        password = "Password123!"

        # Register
        reg_res = self.client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "full_name": f"LoadTest User {random_suffix}"},
        )
        if reg_res.status_code == 201:
            self.token = reg_res.json().get("access_token")
        else:
            # Try login if already registered
            login_res = self.client.post(
                "/api/v1/auth/login",
                data={"username": email, "password": password},
            )
            if login_res.status_code == 200:
                self.token = login_res.json().get("access_token")

    @property
    def headers(self):
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    @task(5)
    def get_subscriptions(self):
        """Core Endpoint #2: GET /api/v1/subscriptions"""
        self.client.get(
            "/api/v1/subscriptions?page=1&size=20",
            headers=self.headers,
            name="/api/v1/subscriptions [list]",
        )

    @task(4)
    def get_upcoming_renewals(self):
        """Core Endpoint #6: GET /api/v1/renewals/upcoming"""
        self.client.get(
            "/api/v1/renewals/upcoming?days=30",
            headers=self.headers,
            name="/api/v1/renewals/upcoming",
        )

    @task(4)
    def get_expenses_report(self):
        """Core Endpoint #7: GET /api/v1/expenses/report"""
        self.client.get(
            "/api/v1/expenses/report",
            headers=self.headers,
            name="/api/v1/expenses/report",
        )

    @task(3)
    def get_analytics_summary(self):
        """Cached Analytics Endpoint: GET /api/v1/analytics/summary"""
        self.client.get(
            "/api/v1/analytics/summary",
            headers=self.headers,
            name="/api/v1/analytics/summary",
        )

    @task(2)
    def get_spending_trends(self):
        """Trends endpoint: GET /api/v1/analytics/trends"""
        self.client.get(
            "/api/v1/analytics/trends",
            headers=self.headers,
            name="/api/v1/analytics/trends",
        )

    @task(1)
    def ai_query(self):
        """Core Endpoint #8: POST /api/v1/ai/query"""
        queries = [
            "What is my total monthly subscription expense?",
            "Which subscriptions are renewing this month?",
            "What is my most expensive active subscription?",
            "How can I optimize my subscription spending?",
        ]
        self.client.post(
            "/api/v1/ai/query",
            json={"question": random.choice(queries)},
            headers=self.headers,
            name="/api/v1/ai/query",
        )

    @task(1)
    def crud_lifecycle(self):
        """Core Endpoints #1, #3, #4, #5: Create, Read, Update, Delete subscription"""
        # Create
        create_res = self.client.post(
            "/api/v1/subscriptions",
            json={
                "name": f"Temp Sub {random.randint(100, 9999)}",
                "cost": round(random.uniform(5.99, 49.99), 2),
                "billing_cycle": "monthly",
                "next_renewal_date": "2026-12-15",
                "category_id": 1,
                "status": "active",
            },
            headers=self.headers,
            name="/api/v1/subscriptions [create]",
        )
        if create_res.status_code == 201:
            sub_id = create_res.json().get("id")
            # Read single
            self.client.get(
                f"/api/v1/subscriptions/{sub_id}",
                headers=self.headers,
                name="/api/v1/subscriptions/{id} [get]",
            )
            # Update
            self.client.put(
                f"/api/v1/subscriptions/{sub_id}",
                json={"cost": 19.99},
                headers=self.headers,
                name="/api/v1/subscriptions/{id} [update]",
            )
            # Delete
            self.client.delete(
                f"/api/v1/subscriptions/{sub_id}",
                headers=self.headers,
                name="/api/v1/subscriptions/{id} [delete]",
            )
