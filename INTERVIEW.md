# Technical Interview Preparation Guide

This document contains detailed, fresher-friendly answers to technical interview questions about the **Subscription Renewal and Expense Tracker**, Java 17 fundamentals, Spring Boot 3, REST APIs, relational database design, Redis caching, and automated testing.

---

## 📑 Table of Contents
1. [Project Overview & Core Problem](#1-project-overview--core-problem)
2. [Java Core & Financial Math Questions](#2-java-core--financial-math-questions)
3. [Date Boundary & Leap Year Handling](#3-date-boundary--leap-year-handling)
4. [Spring Boot & Architecture Questions](#4-spring-boot--architecture-questions)
5. [Database & JPA Questions](#5-database--jpa-questions)
6. [Redis Caching & Invalidation Strategy](#6-redis-caching--invalidation-strategy)
7. [Testing & Quality Assurance](#7-testing--quality-assurance)
8. [Resume Claim Verification Checklist](#8-resume-claim-verification-checklist)

---

## 1. Project Overview & Core Problem

### Q1. Tell me about your project.
**Answer:**
> "I built the **Subscription Renewal and Expense Tracker** using Java 17, Spring Boot 3, MySQL, and Redis. It is a full-stack web application designed to solve two core challenges in managing recurring digital subscriptions:
> 1. Accurately projecting future renewal dates across calendar boundary conditions such as leap years and month ends (e.g., January 31 rolling into February 28 or 29).
> 2. Normalizing disparate billing cycles (weekly, monthly, quarterly, annual) into a single monthly equivalent using exact `BigDecimal` arithmetic.
> 
> The application exposes 8 RESTful API endpoints, caches read-heavy spending aggregations in Redis with automatic eviction on data changes, persists data in MySQL with composite indexes, and includes a responsive frontend dashboard."

### Q2. What problem does it solve?
**Answer:**
> "Individuals and teams often manage recurring software subscriptions across different cadences without visibility into true monthly costs. Summing a $120 annual subscription with a $10 weekly subscription without normalization gives misleading spend figures. Furthermore, recurring renewals often drift across month-end dates. This application automates date projections and standardizes spending calculations."

---

## 2. Java Core & Financial Math Questions

### Q3. Why did you use `BigDecimal` instead of `double` or `float` for subscription costs?
**Answer:**
> "Binary floating-point types (`double` and `float`) cannot accurately represent decimal fractions like 0.1 because standard IEEE 754 floating-point arithmetic represents numbers in base 2. In cumulative financial calculations, this introduces binary rounding errors. `BigDecimal` provides arbitrary-precision signed decimal numbers, allowing explicit specification of scale (2 decimal places) and rounding mode (`RoundingMode.HALF_UP`)."

### Q4. How does your normalization formula work?
**Answer:**
> "All billing cadences are converted to a monthly equivalent:
> - **Weekly:** `amount * 52 / 12`
> - **Bi-Weekly:** `amount * 26 / 12`
> - **Monthly:** `amount * 1`
> - **Quarterly:** `amount / 3`
> - **Semi-Annually:** `amount / 6`
> - **Annually:** `amount / 12`
> 
> Annual expenditure is computed by multiplying the total normalized monthly spend by 12."

---

## 3. Date Boundary & Leap Year Handling

### Q5. How does your renewal calculation engine handle month-end dates and leap years?
**Answer:**
> "In `RenewalCalculator.java`, I utilized Java 8+ `java.time.LocalDate`:
> 1. **Month-End Clamping:** When adding 1 month to January 31 using `plusMonths(1)`, Java automatically clamps the result to the last valid day of February (Feb 28 in non-leap years, or Feb 29 in a leap year).
> 2. **Leap Year Annual Renewals:** If a subscription starts on February 29 (a leap day), `plusYears(1)` projects deterministically to February 28 of the following non-leap year.
> 3. **Historical Start Dates:** If a subscription was started in the past, `projectUpcomingRenewalDate` iteratively advances the cadence until the next renewal is greater than or equal to the current reference date."

---

## 4. Spring Boot & Architecture Questions

### Q6. Walk me through your application architecture.
**Answer:**
> "The application follows the classic N-tier layered architecture:
> - **Presentation Layer:** `@RestController` handles HTTP requests, validates incoming DTOs using Jakarta Validation (`@Valid`), and maps responses.
> - **Service Layer:** Encapsulates business logic, transactional boundaries (`@Transactional`), and Redis caching annotations (`@Cacheable`, `@CacheEvict`).
> - **Persistence Layer:** Spring Data JPA repositories extend `JpaRepository` and define indexed query methods.
> - **Database Layer:** MySQL stores entities with relational constraints and indexes.
> - **Caching Layer:** Redis stores precomputed summary and upcoming renewal lists."

---

## 5. Database & JPA Questions

### Q7. Why did you add composite indexes on MySQL?
**Answer:**
> "The dashboard frequently queries upcoming renewals within a 30-day window filtered by `status = 'ACTIVE'` and sorted by `nextRenewalDate ASC`. 
> 
> A single index on `status` has very poor selectivity because the vast majority of records are active. By creating a composite index `idx_sub_renewal_status (next_renewal_date, status)`, MySQL can satisfy the date range filter and status check directly via an index range scan."

---

## 6. Redis Caching & Invalidation Strategy

### Q8. What caching pattern did you implement, and how do you handle cache invalidation?
**Answer:**
> "I implemented the **Cache-Aside pattern**:
> 1. **Read Path:** The service method is annotated with `@Cacheable`. Spring first checks Redis for the key. If found (cache hit), the cached JSON is deserialized and returned without touching MySQL. If not found (cache miss), the database is queried, the result is calculated, and it is stored in Redis.
> 2. **Write Path:** Whenever a subscription is created, updated, or deleted, `@CacheEvict(allEntries = true)` purges the affected cache namespaces (`monthlySummary`, `categorySummary`, `upcomingRenewals`). This prevents stale data reads."

---

## 7. Testing & Quality Assurance

### Q9. How did you test your application?
**Answer:**
> "I wrote 30 automated tests divided into unit and integration suites:
> - **`RenewalCalculatorTest` (12 tests):** Pure unit tests covering leap years (Feb 29), month-end dates (Jan 31, Mar 31), all 6 billing frequencies, and normalization math.
> - **`SubscriptionServiceTest` & `ExpenseServiceTest` (10 tests):** Mockito unit tests verifying business logic, CRUD interactions, and exceptions (`ResourceNotFoundException`).
> - **`SubscriptionControllerTest` & `ExpenseControllerTest` (8 tests):** `@WebMvcTest` integration tests verifying HTTP status codes (`201`, `200`, `204`, `400`, `404`) and JSON serialization using `MockMvc`."

---

## 8. Resume Claim Verification Checklist

| Resume Bullet Claim | Actual Code File | Test Verification |
| :--- | :--- | :--- |
| **Java 17 & Spring Boot REST APIs** | `SubscriptionController.java`, `ExpenseController.java` | `SubscriptionControllerTest.java` |
| **Renewal Calculation Engine** | `RenewalCalculator.java` | `RenewalCalculatorTest.java` (12 tests) |
| **MySQL JPA Persistence & Indexing** | `Subscription.java`, `SubscriptionRepository.java`, `schema.sql` | `SubscriptionServiceTest.java` |
| **Redis Caching & `@CacheEvict`** | `RedisConfig.java`, `SubscriptionServiceImpl.java`, `ExpenseServiceImpl.java` | Cache eviction hooks in service layer |
| **JUnit 5 & Mockito Testing** | `src/test/java/com/tracker/` | 30 passed tests via `mvn test` |
| **Responsive Web Dashboard** | `static/index.html`, `static/css/styles.css`, `static/js/app.js` | Browser dashboard on port 8080 |
