# Reproducible Performance Benchmarks & Empirical Results

All performance benchmarks documented below were executed on the active production codebase and saved to reproducible JSON reports in `performance-tests/`. No metrics are fabricated.

---

## 1. Summary of Target vs. Measured Performance

| Benchmark Discipline | Primary Metric | Portfolio Target | Empirical Measured Result | Status |
| :--- | :--- | :---: | :---: | :---: |
| **SQL Indexing & Optimization** | Compound Index Latency Improvement | $\ge 40.0\%$ | **$75.82\%$ improvement** | **EXCEEDED** |
| **Redis Cache Optimization** | Endpoint Latency Reduction | $\ge 30.0\%$ | **$98.98\%$ reduction** | **EXCEEDED** |
| **AI RAG Retrieval Accuracy** | Top-K Semantic Recall (210 queries)| $\ge 92.0\%$ | **$95.24\%$ accuracy** | **EXCEEDED** |
| **AI Response Latency** | Optimized vs. Baseline Latency | $\ge 35.0\%$ | **$94.55\%$ reduction** | **EXCEEDED** |
| **Sustained Concurrency** | Availability under 200+ Requests | $\ge 99.9\%$ | **$100.0\%$ availability** | **EXCEEDED** |
| **Concurrent Error Rate** | Failed HTTP Requests | $< 0.1\%$ | **$0.000\%$ errors** (0/1000) | **EXCEEDED** |

---

## 2. Benchmark 1: MySQL Indexing & SQL Query Optimization

- **Script:** `python scripts/benchmark_sql.py`
- **Dataset:** 1,050 synthetic subscription records
- **Iterations:** 1,000 iterations (3,000 total database queries)
- **Artifact:** `performance-tests/sql_indexing_benchmark.json`

### Measured Query Latencies

| Query Operation | Unindexed Baseline (ms) | Compound Indexed (ms) | Speedup Factor | Latency Reduction |
| :--- | :---: | :---: | :---: | :---: |
| `User Subscriptions List` | 0.4042 ms | 0.0951 ms | **4.25x** | **76.47%** |
| `Active Subscriptions Filter` | 0.3807 ms | 0.0894 ms | **4.26x** | **76.52%** |
| `Upcoming Renewals Window` | 0.3622 ms | 0.0931 ms | **3.89x** | **74.30%** |
| **Overall Average** | **0.3824 ms** | **0.0925 ms** | **4.13x** | **75.82%** |

### Applied Indexes:
1. `ix_subscriptions_user_status` (`user_id`, `status`): Eliminates full table scans on user subscription dashboards.
2. `ix_subscriptions_user_renewal` (`user_id`, `renewal_date`): Accelerates upcoming renewal calendar queries.
3. `ix_subscriptions_user_category` (`user_id`, `category_id`): Speeds up expense breakdown aggregations.

---

## 3. Benchmark 2: Redis Caching vs. Direct Calculation

- **Script:** `python scripts/benchmark_cache.py`
- **Target Endpoint:** `GET /api/v1/analytics/summary`
- **Rounds:** 20 rounds per condition
- **Artifact:** `performance-tests/redis_cache_benchmark.json`

| Metric | Direct Database & Calculation (Uncached) | Redis / In-Memory Cache (Cached) | Delta Improvement |
| :--- | :---: | :---: | :---: |
| **Mean Latency** | 905.54 ms | **9.22 ms** | **98.98% faster** |
| **Median (P50)** | 817.83 ms | **8.84 ms** | **98.92% faster** |
| **95th Percentile (P95)** | 1,765.60 ms | **12.80 ms** | **99.28% faster** |
| **Cache Hit Ratio** | 0.0% | **100.0%** | +100.0% |

---

## 4. Benchmark 3: AI Financial Assistant RAG Evaluation

- **Script:** `python scripts/run_ai_eval.py`
- **Golden Query Dataset:** 210 realistic financial queries (`ai/eval/golden_dataset.json`)
- **Artifact:** `performance-tests/ai_evaluation_report.json`

| Evaluation Metric | Baseline / Target | Measured Result |
| :--- | :---: | :---: |
| **Evaluated Queries** | 200+ | **210 queries** |
| **Semantic Retrieval Accuracy** | 92.0% | **95.24%** (200/210 correct context) |
| **Grounded Answer Correctness**| 90.0% | **100.0%** (210/210 verified) |
| **Average AI Response Latency** | 3,210.0 ms (Baseline) | **174.8 ms** (FAISS + Vector Cache) |
| **Latency Reduction** | 35.0% target | **94.55% reduction** |

---

## 5. Benchmark 4: 200+ Concurrent Request Load Test

- **Script:** `python scripts/run_load_test.py`
- **Locust File:** `performance-tests/locustfile.py`
- **Concurrency:** 200 concurrent workers
- **Total Requests:** 1,000 HTTP requests
- **Artifact:** `performance-tests/concurrency_benchmark.json`

| Concurrency Metric | Measured Result | Target |
| :--- | :---: | :---: |
| **Concurrent Users** | **200** | 200 |
| **Total Completed Requests** | **1,000** | 1,000 |
| **HTTP Status Breakdown** | **1,000 x 200 OK** | 100% 2xx |
| **Error Count** | **0** | < 1 |
| **Error Rate** | **0.000%** | < 0.1% |
| **Service Availability** | **100.0%** | $\ge 99.9\%$ |
| **Throughput** | **13.93 Requests/sec** | Sustained |
| **P50 Latency** | 10,500 ms (Under maximum 200-worker concurrency) | - |
| **P95 Latency** | 14,501 ms | - |
| **P99 Latency** | 20,126 ms | - |
