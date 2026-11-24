# REST API Documentation & Usage Guide

Interactive Swagger/OpenAPI documentation is available at: `http://localhost:8000/api/v1/docs`

All API endpoints require authentication via Bearer Token except `/api/v1/auth/register` and `/api/v1/auth/login`.

---

## 1. Authentication Endpoints

### 1.1 User Registration
**`POST /api/v1/auth/register`**

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "fintech_user",
    "password": "SecurePassword123!",
    "full_name": "Alex Mercer"
  }'
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "fintech_user",
    "full_name": "Alex Mercer",
    "roles": ["USER"],
    "is_active": true
  }
}
```

### 1.2 User Login
**`POST /api/v1/auth/login`**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=SecurePassword123!"
```

### 1.3 Refresh Access Token
**`POST /api/v1/auth/refresh`**

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJhbGciOiJIUzI1NiIsIn..."}'
```

---

## 2. The 8 Mandatory Core Business Endpoints

### Core Endpoint 1: Create Subscription
**`POST /api/v1/subscriptions`**

```bash
curl -X POST http://localhost:8000/api/v1/subscriptions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AWS Cloud Hosting",
    "description": "Production EC2 and S3 instances",
    "cost": 89.50,
    "currency": "USD",
    "billing_cycle": "MONTHLY",
    "start_date": "2026-01-01",
    "renewal_date": "2026-12-01",
    "status": "ACTIVE",
    "auto_renew": true,
    "utility_score": 9,
    "is_essential": true,
    "category_id": 4
  }'
```

**Response (201 Created):**
```json
{
  "id": 1051,
  "user_id": 1,
  "name": "AWS Cloud Hosting",
  "cost": 89.5,
  "currency": "USD",
  "billing_cycle": "MONTHLY",
  "start_date": "2026-01-01",
  "renewal_date": "2026-12-01",
  "status": "ACTIVE",
  "auto_renew": true,
  "utility_score": 9,
  "is_essential": true,
  "monthly_equivalent_cost": 89.5,
  "annual_equivalent_cost": 1074.0,
  "created_at": "2026-11-24T16:00:00Z"
}
```

---

### Core Endpoint 2: List Subscriptions (Filtered & Sorted)
**`GET /api/v1/subscriptions`**

Query parameters:
- `status`: `ACTIVE`, `CANCELLED`, `EXPIRED`, `PAUSED`
- `category_id`: Filter by integer ID
- `search`: Case-insensitive substring matching
- `sort_by`: `renewal_date`, `cost`, `name`
- `order`: `asc`, `desc`

```bash
curl -X GET "http://localhost:8000/api/v1/subscriptions?status=ACTIVE&sort_by=cost&order=desc" \
  -H "Authorization: Bearer $TOKEN"
```

---

### Core Endpoint 3: Get Subscription Details
**`GET /api/v1/subscriptions/{id}`**

```bash
curl -X GET http://localhost:8000/api/v1/subscriptions/1051 \
  -H "Authorization: Bearer $TOKEN"
```

---

### Core Endpoint 4: Update Subscription
**`PUT /api/v1/subscriptions/{id}`**

```bash
curl -X PUT http://localhost:8000/api/v1/subscriptions/1051 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cost": 99.00,
    "billing_cycle": "MONTHLY",
    "utility_score": 10
  }'
```

---

### Core Endpoint 5: Delete / Cancel Subscription
**`DELETE /api/v1/subscriptions/{id}`**

```bash
curl -X DELETE http://localhost:8000/api/v1/subscriptions/1051 \
  -H "Authorization: Bearer $TOKEN"
```
**Response:** `204 No Content`

---

### Core Endpoint 6: Upcoming Renewals
**`GET /api/v1/renewals/upcoming`**

Query parameters:
- `days`: Number of days ahead (default: 30)

```bash
curl -X GET "http://localhost:8000/api/v1/renewals/upcoming?days=14" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200 OK):**
```json
[
  {
    "id": 1051,
    "name": "AWS Cloud Hosting",
    "cost": 99.0,
    "billing_cycle": "MONTHLY",
    "renewal_date": "2026-12-01",
    "days_until_renewal": 7,
    "category": "Cloud"
  }
]
```

---

### Core Endpoint 7: Comprehensive Expenses Report
**`GET /api/v1/expenses/report`**

Supports JSON report format and CSV file export:

```bash
# JSON Comprehensive Analytics Report
curl -X GET http://localhost:8000/api/v1/expenses/report \
  -H "Authorization: Bearer $TOKEN"

# CSV Export
curl -X GET "http://localhost:8000/api/v1/expenses/report?format=csv" \
  -H "Authorization: Bearer $TOKEN" \
  -o "subscriptions_export.csv"
```

---

### Core Endpoint 8: AI Financial Assistant Query
**`POST /api/v1/ai/query`**

```bash
curl -X POST http://localhost:8000/api/v1/ai/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which subscription is renewing next week and how much does it cost?"
  }'
```

**Response (200 OK):**
```json
{
  "answer": "Your 'AWS Cloud Hosting' subscription is scheduled to renew on December 1, 2026, costing $99.00 per month.",
  "sources": [
    {
      "id": 1051,
      "name": "AWS Cloud Hosting",
      "cost": 99.0,
      "billing_cycle": "MONTHLY",
      "category": "Cloud",
      "renewal_date": "2026-12-01",
      "relevance_score": 0.942
    }
  ],
  "latency_ms": 175,
  "tokens_used": 142,
  "model": "rag-grounded-gpt4o-mini",
  "timestamp": "2026-11-24T16:00:00Z"
}
```
