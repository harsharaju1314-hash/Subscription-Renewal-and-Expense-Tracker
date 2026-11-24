# Platform Architecture & Design Documentation

## 1. System Overview

The **Subscription Renewal and Expense Analytics Platform** is structured as a decoupled, multi-service architecture designed for high throughput, sub-millisecond cache hits, deterministic financial precision, and contextual AI-driven insights.

```mermaid
flowchart TD
    User(["Client / Web Browser"]) -->|HTTPS 443| Nginx["Nginx Reverse Proxy & Static Host"]
    
    subgraph UI ["Frontend Tier"]
        Nginx -->|Serves SPA Bundle| Angular["Angular 17+ Dashboard & WCAG 2.1 AA UI"]
    end

    subgraph CoreBackend ["FastAPI Core Gateway Tier (Port 8000)"]
        Nginx -->|/api/v1/| API["FastAPI Application"]
        API --> AuthRouter["Auth & RBAC Middleware"]
        API --> SubRouter["Subscription CRUD & Lifecycle"]
        API --> AIClient["AI Conversational Agent Router"]
        API --> ObsRouter["Prometheus & Healthcheck Engine"]
    end

    subgraph AnalyticsTier ["Flask Analytics Microservice Tier (Port 5001)"]
        API -->|Authenticated Internal HTTP| FlaskService["Flask Calculation Engine"]
        FlaskService --> DecimalCalc["Decimal-Precision Arithmetic"]
        FlaskService --> CSVExport["Streaming CSV Exporter"]
    end

    subgraph StorageTier ["Data & Caching Tier"]
        API <-->|SQLAlchemy ORM + Compound Indexes| MySQL[("MySQL 8.0 Relational DB")]
        API <-->|LRU / Distributed Key-Value| Redis[("Redis 7 In-Memory Cache")]
        API <-->|L2 / Cosine Similarity Index| FAISS[("FAISS Vector Database")]
    end

    subgraph ObservabilityTier ["Monitoring Tier"]
        Prometheus["Prometheus Server (Port 9090)"] -->|Scrapes /metrics| API
        Prometheus -->|Scrapes /metrics| FlaskService
        Grafana["Grafana Visualizer (Port 3000)"] -->|Queries| Prometheus
    end

    subgraph CloudAI ["AI Synthesis Tier"]
        AIClient -->|Prompt + Context| OpenAI["OpenAI API (GPT-4o-mini)"]
    end
```

---

## 2. Sequence Diagrams

### 2.1 User Authentication & Token Refresh Flow

```mermaid
sequenceDiagram
    autonumber
    actor Client as User / Browser
    participant API as FastAPI Gateway
    participant DB as MySQL DB
    participant Cache as Redis Cache

    Client->>API: POST /api/v1/auth/login (email, password)
    API->>DB: Query User by email
    DB-->>API: User Record + Hashed Password
    API->>API: Verify password with bcrypt
    API->>API: Issue Access Token (30m) & Refresh Token (7d)
    API-->>Client: 200 OK {access_token, refresh_token, user_profile}

    Note over Client,API: After 30 minutes (Access token expires)
    Client->>API: POST /api/v1/auth/refresh {refresh_token}
    API->>API: Decode and validate refresh token signature
    API->>DB: Verify user is active
    API-->>Client: 200 OK {new_access_token, new_refresh_token}
```

### 2.2 Subscription CRUD & Cache Invalidation

```mermaid
sequenceDiagram
    autonumber
    actor Client as User
    participant API as FastAPI Gateway
    participant Cache as Redis Cache
    participant DB as MySQL DB
    participant FAISS as FAISS Vector Store

    Client->>API: POST /api/v1/subscriptions {name, cost, billing_cycle, renewal_date}
    API->>DB: Begin Transaction: INSERT INTO subscriptions
    DB-->>API: Generated Subscription ID
    API->>DB: Commit Transaction
    API->>Cache: Invalidate user cache keys (user:{id}:analytics:*)
    API->>FAISS: Add vector embedding for new subscription
    API-->>Client: 201 Created {SubscriptionResponse}
```

### 2.3 Grounded RAG AI Assistant Execution

```mermaid
sequenceDiagram
    autonumber
    actor Client as User
    participant API as FastAPI Backend
    participant DB as MySQL Database
    participant FAISS as FAISS Vector Index
    participant LLM as OpenAI GPT-4o-mini

    Client->>API: POST /api/v1/ai/query {"query": "What is my total monthly spend?"}
    API->>API: Sanitize query against prompt-injection patterns
    API->>FAISS: Query semantic embedding space (L2 / Cosine Similarity)
    FAISS-->>API: Top-K Relevant Subscription Documents
    API->>DB: Authorize document ownership (user_id constraint)
    API->>API: Execute deterministic SQL calculator (No LLM math hallucination)
    API->>LLM: Construct grounded prompt with actual verified figures
    LLM-->>API: Grounded, formatted answer synthesis
    API->>DB: Save conversation log (AIConversation)
    API-->>Client: 200 OK {answer, sources, latency_ms}
```

---

## 3. Database Entity Relationship (ER) Model

```mermaid
erDiagram
    USERS ||--o{ USER_ROLES : has
    ROLES ||--o{ USER_ROLES : assigned_to
    USERS ||--o{ SUBSCRIPTIONS : owns
    CATEGORIES ||--o{ SUBSCRIPTIONS : categorizes
    SUBSCRIPTIONS ||--o{ RENEWAL_REMINDERS : triggers
    USERS ||--o{ BUDGETS : defines
    USERS ||--o{ AI_CONVERSATIONS : conducts

    USERS {
        int id PK
        string email UK
        string username UK
        string hashed_password
        string full_name
        boolean is_active
        datetime created_at
    }

    ROLES {
        int id PK
        string name UK
        string description
    }

    SUBSCRIPTIONS {
        int id PK
        int user_id FK
        int category_id FK
        string name
        decimal cost
        string currency
        enum billing_cycle
        date start_date
        date renewal_date
        enum status
        boolean auto_renew
        int utility_score
        boolean is_essential
    }

    CATEGORIES {
        int id PK
        string name UK
        string icon
        string color
    }

    BUDGETS {
        int id PK
        int user_id FK
        decimal monthly_limit
        int alert_threshold_pct
    }

    RENEWAL_REMINDERS {
        int id PK
        int subscription_id FK
        date reminder_date
        boolean is_sent
        datetime sent_at
    }

    AI_CONVERSATIONS {
        int id PK
        int user_id FK
        string query
        string response
        int latency_ms
        datetime created_at
    }
```
