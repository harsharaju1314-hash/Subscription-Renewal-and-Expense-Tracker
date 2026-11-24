# Automated Testing & Quality Assurance Suite

The platform maintains an automated test suite executed with `pytest` and load-tested with `Locust`.

---

## 1. Test Suite Summary

- **Total Automated Pytest Tests:** 68 passing tests
- **Pass Rate:** 100.0%
- **Execution Time:** ~16 seconds
- **Test Modules:** 10 dedicated test suites

### Test Module Matrix

| Test Module | Test Count | Scope & Behaviors Verified |
| :--- | :---: | :--- |
| `tests/test_core_api_v1.py` | 14 | 8 core endpoints, refresh token rotation, RBAC enforcement, liveness/readiness probes, input validation |
| `tests/test_flask_analytics.py` | 6 | Flask analytics microservice, inter-service authentication (`X-Internal-Secret`), Decimal calculations, CSV generation |
| `tests/test_auth.py` | 7 | User registration, password hashing validation, login JWT generation, credential rejection, `/me` profile |
| `tests/test_subscriptions.py` | 8 | Subscription CRUD lifecycle, status filters, category filters, upcoming renewal dates |
| `tests/test_cache.py` | 5 | Redis cache set/get, TTL expiration, invalidation on create/delete, fallback logic |
| `tests/test_optimization.py` | 6 | Budget optimization engine, knapsack pruning of low-utility subscriptions, essential retention |
| `tests/test_data_isolation.py` | 5 | Multi-tenant isolation, cross-user access denial (404), RAG vector space isolation per user |
| `tests/test_expense_calculations.py`| 6 | Decimal-precision annual/monthly equivalent costs across all billing cycles, aggregation summaries |
| `tests/test_rag_pipeline.py` | 5 | Semantic embedding generation, FAISS indexing, top-K retrieval similarity, index updates |
| `tests/test_ai_service.py` | 6 | AI assistant endpoint responses, golden query matching, reindexing endpoints |

---

## 2. Running Automated Tests

Run the full pytest suite:

```bash
pytest tests/ -v
```

Run specific test modules:

```bash
pytest tests/test_core_api_v1.py -v
pytest tests/test_flask_analytics.py -v
```

Generate HTML and XML coverage reports:

```bash
pytest --cov=backend/app --cov=analytics_service/app --cov=ai --cov-report=html --cov-report=xml tests/
```

---

## 3. Load Testing with Locust

The platform includes a Locust load testing suite (`performance-tests/locustfile.py`) and an automated runner (`scripts/run_load_test.py`):

```bash
python scripts/run_load_test.py
```

To run Locust with its interactive web interface:

```bash
locust -f performance-tests/locustfile.py --host http://localhost:8000
```
Then navigate to `http://localhost:8089` to configure user concurrency and spawn rates.
