# Subscription Renewal and Expense Tracker

A full-stack web application designed to track recurring subscriptions, automate renewal date projections across calendar edge cases, normalize recurring expenses across diverse billing cycles, and provide high-performance spending analytics backed by Redis caching.

---

## Overview

Modern software ecosystems involve numerous recurring expenses spanning cloud providers, developer tool licenses, and entertainment services. Subscriptions follow disparate billing cadences (weekly, bi-weekly, monthly, quarterly, semi-annually, annually), creating two primary challenges: tracking upcoming renewals before unreviewed charges occur, and projecting accurate monthly and annual burn rates.

This project delivers a centralized platform featuring a responsive frontend, a layered Spring Boot REST backend, relational persistence via MySQL, and an in-memory caching layer using Redis.

---

## Problem Statement

1. **Renewal Date Drift & Edge Cases**: Naive date addition fails on calendar boundaries (months with 28, 29, 30, or 31 days) and leap years. A subscription renewing on January 31 must resolve to February 28 (or February 29 in a leap year), while leap-year annual renewals (February 29) must transition to February 28 the following year.
2. **Inconsistent Expense Normalization**: Directly summing an annual $120 subscription and a weekly $10 subscription gives a misleading picture of recurring expenditure. Normalization to standard monthly and annual equivalents using exact decimal arithmetic is required.
3. **Database Aggregation Overhead**: Generating aggregate statistics (monthly spending, annual burn rate, and category breakdowns) repeatedly stresses the relational database. A cache-aside caching pattern with automated invalidation is necessary to optimize throughput.

---

## Key Features

- **Subscription Lifecycle Management**: Full CRUD operations for recurring subscriptions, including name, category, amount, currency, billing frequency, and active status.
- **Deterministic Renewal Engine**: Renewal calculations handling standard increments, month-end date clamping, leap years, and iterative alignment from past start dates.
- **Monetary Normalization**: Financial math computed using `BigDecimal` with `RoundingMode.HALF_UP` to prevent binary floating-point precision loss.
- **RESTful API Suite**: 8 documented REST endpoints featuring Jakarta Bean Validation, declarative error responses, sorting, filtering, and pagination.
- **Redis In-Memory Caching**: Cache-aside implementation caching monthly summaries, category distributions, and upcoming renewals, with automated eviction (`@CacheEvict`) on write operations.
- **Responsive Dashboard UI**: Single-page interface built with modern HTML5, CSS3, and native JavaScript `fetch()` that renders live KPI cards, interactive modals, urgency indicators, and category progress bars.
- **Automated Test Coverage**: 30 automated tests spanning pure mathematical/calendar unit tests, Mockito service layer tests, and Spring MVC WebMvcTest controller integration suites.
- **Containerized Architecture**: Multi-stage `Dockerfile` and `docker-compose.yml` defining the application, MySQL 8.4, and Redis 7 services with health checks and volume persistence.

---

## Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Java 17, Spring Boot 3.3.4 (Spring Web, Spring Data JPA, Spring Cache, Validation) |
| **Frontend** | HTML5, CSS3, JavaScript (Fetch API, DOM Manipulation) |
| **Database** | MySQL 8.4 (InnoDB), H2 Database (in-memory dev/test profile) |
| **Caching** | Redis 7, Spring Data Redis, GenericJackson2JsonRedisSerializer |
| **Testing** | JUnit 5, Mockito, AssertJ, Spring Boot Test, Spring MVC Test |
| **Build & Tooling** | Apache Maven 3.9.9, Maven Wrapper (`mvnw`) |
| **DevOps** | Docker, Docker Compose |
| **VCS** | Git, GitHub |

---

## System Architecture / Workflow

The system is built on a standard N-tier architecture:

```
User (Browser UI)
       │
       ▼ [HTTP / JSON via fetch()]
REST Controllers (Presentation Layer)
  ├── SubscriptionController
  ├── ExpenseController
  └── GlobalExceptionHandler
       │
       ▼ [DTOs & Jakarta Validation]
Business Service Layer
  ├── SubscriptionServiceImpl (CRUD & Renewal Engine)
  └── ExpenseServiceImpl (Spend Normalization)
       │
       ├─────────────────────────────────┐
       ▼ [Cache Check / Evict]           ▼ [ORM / SQL]
Redis Cache                       MySQL Database (JPA / Hibernate)
  ├── monthlySummary                └── subscriptions table
  ├── categorySummary                     ├── idx_sub_renewal_status
  └── upcomingRenewals                    ├── idx_sub_category_status
                                          └── idx_sub_status
```

### Request Flow
1. **User Action**: The client sends an HTTP request using JavaScript `fetch()`.
2. **API Controller**: `@RestController` maps the request, enforces input validation via `@Valid`, and delegates to the Service.
3. **Business Logic**: `@Service` computes dates using `RenewalCalculator`, manages transactional state (`@Transactional`), and interacts with the cache.
4. **Cache / Database**:
   - For reads: The service checks Redis via `@Cacheable`. If absent, it queries MySQL through Spring Data JPA, computes the response, and populates the cache.
   - For writes: Data is committed to MySQL, and `@CacheEvict` invalidates outdated cache keys.
5. **Response**: The controller returns standard JSON payloads with appropriate HTTP status codes (`200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `404 Not Found`).

---

## Project Structure

```
Subscription-Renewal-and-Expense-Tracker/
├── .dockerignore
├── .gitignore
├── Dockerfile
├── README.md
├── docker-compose.yml
├── pom.xml
└── src/
    ├── main/
    │   ├── java/
    │   │   └── com/
    │   │       └── tracker/
    │   │           ├── SubscriptionTrackerApplication.java
    │   │           ├── config/
    │   │           │   └── RedisConfig.java
    │   │           ├── controller/
    │   │           │   ├── ExpenseController.java
    │   │           │   └── SubscriptionController.java
    │   │           ├── dto/
    │   │           │   ├── CategoryExpenseDTO.java
    │   │           │   ├── ErrorResponseDTO.java
    │   │           │   ├── MonthlyExpenseSummaryDTO.java
    │   │           │   ├── PagedResponseDTO.java
    │   │           │   ├── SubscriptionRequestDTO.java
    │   │           │   └── SubscriptionResponseDTO.java
    │   │           ├── entity/
    │   │           │   ├── BillingFrequency.java
    │   │           │   ├── Subscription.java
    │   │           │   └── SubscriptionStatus.java
    │   │           ├── exception/
    │   │           │   ├── GlobalExceptionHandler.java
    │   │           │   └── ResourceNotFoundException.java
    │   │           ├── repository/
    │   │           │   └── SubscriptionRepository.java
    │   │           ├── service/
    │   │           │   ├── ExpenseService.java
    │   │           │   ├── SubscriptionService.java
    │   │           │   └── impl/
    │   │           │       ├── ExpenseServiceImpl.java
    │   │           │       └── SubscriptionServiceImpl.java
    │   │           └── util/
    │   │               └── RenewalCalculator.java
    │   └── resources/
    │       ├── application.properties
    │       ├── application-dev.properties
    │       ├── application-mysql.properties
    │       ├── data.sql
    │       ├── schema.sql
    │       └── static/
    │           ├── index.html
    │           ├── css/
    │           └── js/
    └── test/
        ├── java/
        │   └── com/
        │       └── tracker/
        │           ├── controller/
        │           │   ├── ExpenseControllerTest.java
        │           │   └── SubscriptionControllerTest.java
        │           ├── service/
        │           │   ├── ExpenseServiceTest.java
        │           │   └── SubscriptionServiceTest.java
        │           └── util/
        │               └── RenewalCalculatorTest.java
        └── resources/
            └── application-test.properties
```

---

## How It Works

### 1. Renewal Date Calculation Rules
Calculations are executed inside `RenewalCalculator.java` using `java.time.LocalDate`:
- **Weekly / Bi-Weekly**: `baseDate.plusWeeks(1)` or `plusWeeks(2)`.
- **Monthly / Quarterly / Semi-Annually**: `baseDate.plusMonths(N)`. When the start day exceeds the destination month length (e.g., January 31 to February), Java's date implementation clamps the result to the final valid day of the month (Feb 28 in non-leap years, Feb 29 in leap years).
- **Annually**: `baseDate.plusYears(1)`. For leap day contracts (February 29, 2024), the next year resolves deterministically to February 28, 2025.
- **Historical Catch-up**: For subscriptions registered with a past start date, the system iteratively advances the cadence until the next renewal date is greater than or equal to the current reference date.

### 2. Expense Normalization Formula
To aggregate recurring costs into a unified monthly expenditure, the system applies the following formulas using `BigDecimal` with 4 decimal places internally and 2 decimal places in output (`RoundingMode.HALF_UP`):
- `WEEKLY`: `amount * 52 / 12`
- `BI_WEEKLY`: `amount * 26 / 12`
- `MONTHLY`: `amount`
- `QUARTERLY`: `amount / 3`
- `SEMI_ANNUALLY`: `amount / 6`
- `ANNUALLY`: `amount / 12`

Annual projected burn rate is computed as:
$$\text{Annual Expense} = \text{Monthly Normalized Expense} \times 12$$

---

## REST API Endpoints

The backend exposes 8 documented REST endpoints under `/api/v1`:

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `POST` | `/api/v1/subscriptions` | Create a new subscription record with validation and renewal projection |
| `GET` | `/api/v1/subscriptions` | Retrieve paginated, sorted, and filtered subscription list |
| `GET` | `/api/v1/subscriptions/{id}` | Retrieve a single subscription by primary key |
| `PUT` | `/api/v1/subscriptions/{id}` | Update existing subscription details and recalculate renewal date |
| `DELETE` | `/api/v1/subscriptions/{id}` | Delete a subscription record |
| `GET` | `/api/v1/subscriptions/upcoming` | Fetch upcoming renewals within next N days (default 30, cached) |
| `GET` | `/api/v1/expenses/summary` | Get aggregated portfolio monthly & annual spend summary (cached) |
| `GET` | `/api/v1/expenses/by-category` | Get breakdown of normalized expenses grouped by category (cached) |

---

## Database Schema & Indexing

Relational tables are defined in MySQL with InnoDB engine and UTF-8 encoding:

```sql
CREATE TABLE subscriptions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    billing_frequency VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    next_renewal_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    cancellation_date DATE NULL,
    notes VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_positive_amount CHECK (amount > 0.00)
);

CREATE INDEX idx_sub_renewal_status ON subscriptions (next_renewal_date, status);
CREATE INDEX idx_sub_category_status ON subscriptions (category, status);
CREATE INDEX idx_sub_status ON subscriptions (status);
```

### Indexing Rationale
- `idx_sub_renewal_status (next_renewal_date, status)`: Accelerates queries retrieving subscriptions renewing within the next 30 days (`WHERE status = 'ACTIVE' AND next_renewal_date BETWEEN ? AND ?`).
- `idx_sub_category_status (category, status)`: Speeds up category grouping and distribution queries.
- `idx_sub_status (status)`: Quickly isolates active subscriptions from cancelled ones for financial summaries.

---

## Redis Caching Strategy

- **Cache Keys**:
  - `monthlySummary`: Key `'summary'` stores the computed `MonthlyExpenseSummaryDTO`.
  - `categorySummary`: Key `'byCategory'` stores `List<CategoryExpenseDTO>`.
  - `upcomingRenewals`: Key `'upcoming-' + #days` stores `List<SubscriptionResponseDTO>`.
- **TTL**: 10 minutes (600,000 ms) configured via `RedisConfig.java` to prevent stale data buildup.
- **Cache Invalidation**: On write operations (`createSubscription`, `updateSubscription`, `deleteSubscription`), `@CacheEvict(allEntries = true)` purges the affected cache namespaces, ensuring cache consistency.
- **Tradeoff Discussion**:
  - *Advantage*: Aggregation calculations and database joins are executed once and cached, eliminating repetitive full table scans on high-traffic dashboards.
  - *Risk*: Without distributed eviction, multi-instance setups risk serving stale data if database modifications bypass the service layer. In this architecture, service-level `@CacheEvict` ensures cache coherence for application operations.

---

## Installation & Prerequisites

- **Java**: OpenJDK 17 or higher
- **Maven**: Version 3.8+
- **Docker & Docker Compose** (optional, for containerized run)
- **MySQL 8.x & Redis 7.x** (optional for local profile; included in Docker)

---

## Configuration

The application uses Spring Boot profiles to separate development and production environments:

- **`dev` profile (Default)**: Uses in-memory H2 database with MySQL dialect and in-memory cache abstraction. Requires no external services.
- **`mysql` profile**: Connects to external MySQL and Redis services via environment variables:
  - `DB_URL` (default: `jdbc:mysql://localhost:3306/subscription_db`)
  - `DB_USERNAME` (default: `root`)
  - `DB_PASSWORD` (default: `root`)
  - `REDIS_HOST` (default: `localhost`)
  - `REDIS_PORT` (default: `6379`)

---

## Running the Application

### Option 1: Standalone Local Mode (Zero External Dependencies)
Runs with embedded H2 and built-in seed data on port 8080:

```bash
mvn spring-boot:run
```

Access the dashboard at: [http://localhost:8080](http://localhost:8080)  
Access the H2 database console at: [http://localhost:8080/h2-console](http://localhost:8080/h2-console) (JDBC URL: `jdbc:h2:mem:subscription_db`, User: `sa`, Password: empty).

### Option 2: Docker Compose (Full Stack with MySQL & Redis)
Launches the application container, MySQL 8.4, and Redis 7 in a private network:

```bash
docker-compose up --build
```

To stop containers and keep data:
```bash
docker-compose down
```

---

## Testing

The project includes 30 automated tests executed via the Maven Surefire plugin.

```bash
# Run entire test suite
mvn test
```

### Verified Test Results
```
[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.tracker.util.RenewalCalculatorTest
[INFO] Tests run: 12, Failures: 0, Errors: 0, Skipped: 0
[INFO] Running com.tracker.service.SubscriptionServiceTest
[INFO] Tests run: 7, Failures: 0, Errors: 0, Skipped: 0
[INFO] Running com.tracker.service.ExpenseServiceTest
[INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0
[INFO] Running com.tracker.controller.SubscriptionControllerTest
[INFO] Tests run: 6, Failures: 0, Errors: 0, Skipped: 0
[INFO] Running com.tracker.controller.ExpenseControllerTest
[INFO] Tests run: 2, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] Results:
[INFO] Tests run: 30, Failures: 0, Errors: 0, Skipped: 0
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
```

### Test Scope
1. **`RenewalCalculatorTest`**: Verifies weekly, bi-weekly, monthly, quarterly, semi-annually, annually, month-end clamping (Jan 31 to Feb 28/29), leap year handling (Feb 29 to Feb 28), and normalization math.
2. **`SubscriptionServiceTest`**: Tests business operations, repository interaction, error handling (`ResourceNotFoundException`), and date recalculation on cadence modification.
3. **`ExpenseServiceTest`**: Tests monthly/annual aggregations and category percentage distributions.
4. **`SubscriptionControllerTest` & `ExpenseControllerTest`**: Tests REST status codes (`201`, `200`, `204`, `400`, `404`) and JSON serialization using MockMvc.

---

## Sample Usage

### 1. Create a Subscription
```bash
curl -X POST http://localhost:8080/api/v1/subscriptions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Datadog Pro",
    "category": "CLOUD",
    "amount": 15.00,
    "currency": "USD",
    "billingFrequency": "MONTHLY",
    "startDate": "2026-01-15",
    "notes": "Infrastructure monitoring"
  }'
```

### 2. Retrieve Portfolio Spending Summary
```bash
curl http://localhost:8080/api/v1/expenses/summary
```
**Response**:
```json
{
  "totalActiveSubscriptions": 8,
  "totalMonthlyExpense": 223.56,
  "totalAnnualExpense": 2682.72,
  "currency": "USD",
  "calculatedAt": "2026-10-15T20:06:30"
}
```

---

## What I Learned

- **Defensive Date Engineering**: Implemented deterministic date handling using `java.time.LocalDate` rather than legacy date classes, properly addressing calendar boundaries like February 29 and month-end dates.
- **Financial Precision in Java**: Applied `BigDecimal` with explicit scale and rounding mode (`HALF_UP`) across all conversion formulas, avoiding floating-point inaccuracies inherent in `double` and `float`.
- **Cache-Aside Architecture & Invalidation**: Integrated Spring Cache with Redis to accelerate read-heavy aggregation queries, while ensuring cache consistency through automated `@CacheEvict` annotations on write paths.
- **RESTful API Design**: Built clean, resource-oriented endpoints with proper HTTP semantics, centralized exception mapping via `@RestControllerAdvice`, and declarative DTO validation.
- **Layered Enterprise Architecture**: Maintained strict separation between Controllers, Services, Repositories, and Entities to guarantee code maintainability and testability.

---

## Future Improvements

- [ ] **Email / Webhook Alerts**: Dispatch notification reminders 3 days prior to renewal dates.
- [ ] **Multi-Currency Conversion**: Integrate an exchange-rate provider to normalize foreign currency expenses into a single target currency.
- [ ] **Role-Based Authentication**: Integrate Spring Security with JWT for multi-tenant user isolation.

---

## Author

**Harshavardhan Varma**  
- Email: [harsharaju1314@gmail.com](mailto:harsharaju1314@gmail.com)  
- GitHub: [@harsharaju1314-hash](https://github.com/harsharaju1314-hash)  
- Repository: [Subscription-Renewal-and-Expense-Tracker](https://github.com/harsharaju1314-hash/Subscription-Renewal-and-Expense-Tracker)
