# AI Data Platform - Phase 1 Architecture Design

## 1. Executive Summary

AI Data Platform is a production-oriented internal analytics application that allows business users to ask questions in natural language and receive SQL-backed insights from multiple SQL databases. The system is designed as a three-layer application:

- React frontend for user interaction and visualization
- FastAPI backend for orchestration, validation, persistence, and observability
- External services for databases and LLM providers

The architecture is intentionally modular so that the backend can evolve from a prototype into a robust enterprise service without rewriting core abstractions.

---

## 2. Architectural Goals

The design prioritizes:

- Extensibility for new LLM providers and SQL databases
- Maintainability through clear separation of concerns
- Testability through dependency injection and interface-based abstractions
- Modularity so each subsystem can evolve independently
- Observability through structured logs, correlation IDs, and metrics
- Production readiness through validation, error handling, and environment-based configuration

---

## 3. High-Level Architecture

```text
User -> React Frontend -> FastAPI Backend -> Database Connectors
                                      -> LLM Providers
                                      -> Observability Layer
                                      -> Persistence Layer
```

The frontend never talks directly to databases or LLM providers. All business logic and orchestration remain in the FastAPI backend.

---

## 4. Backend Architecture

### 4.1 Core Principles

The backend follows Clean Architecture and SOLID principles:

- Controllers remain thin and only handle HTTP concerns
- Service layer contains orchestration and business rules
- Repositories abstract persistence concerns
- Providers expose interchangeable interfaces for LLMs and databases
- Dependency injection ensures loose coupling and easy testing

### 4.2 Proposed Package Structure

```text
backend/
  app/
    api/
      routes/
      dependencies/
      schemas/
    core/
      config/
      exceptions/
      logging/
      middleware/
    services/
      chat/
      query/
      connection/
      history/
      metrics/
    repositories/
      sql/
      conversation/
      metrics/
    providers/
      llm/
        base.py
        gemini.py
        openai.py
      database/
        base.py
        postgres.py
        mysql.py
        sqlite.py
    domain/
      models/
      value_objects/
    usecases/
      generate_sql_usecase.py
      execute_query_usecase.py
      manage_connection_usecase.py
    observability/
      metrics.py
      tracing.py
    tests/
      unit/
      integration/
```

### 4.3 Why This Structure

This layout separates infrastructure concerns from business use cases. It allows the team to add providers, repositories, and new use cases without disturbing the rest of the system. The service layer owns orchestration, while the provider layer remains replaceable.

---

## 5. SQL Connector Architecture

### 5.1 Design Choice

A provider-based connector architecture is used so the application can support multiple SQL databases without hardcoded branching.

```text
DatabaseConnector
  ├── PostgresConnector
  ├── MySQLConnector
  └── SQLiteConnector
```

### 5.2 Interface

Each connector implements a common interface with the following capabilities:

- connect()
- validate_connection()
- execute_query()
- inspect_schema()
- list_tables()
- list_columns()

### 5.3 Why This Is the Right Design

This avoids business logic like:

```python
if database_type == "postgres":
    ...
```

Instead, the application resolves the correct connector through a factory or dependency injection container. That makes the core application database-agnostic and keeps provider-specific logic isolated.

### 5.4 Extension Strategy

Adding SQL Server, Oracle, or BigQuery later requires:

1. Implementing a new connector class
2. Registering it in the connector factory or DI container
3. Adding minimal configuration mapping

---

## 6. LLM Provider Architecture

### 6.1 Design Choice

The LLM layer is also provider-based to allow future support for Claude, Azure OpenAI, Ollama, and others with minimal friction.

```text
LLMProvider
  ├── GeminiProvider
  └── OpenAIProvider
```

### 6.2 Interface

Each provider exposes:

- generate()
- stream()
- structured_output()

### 6.3 Why This Is the Right Design

The backend should not depend on Gemini or OpenAI directly. Instead, it should depend on an abstraction. This keeps the orchestration layer stable while allowing provider-specific implementations to evolve independently.

### 6.4 Configuration Strategy

All provider configuration comes from environment variables.

Examples:

- OPENAI_API_KEY
- GEMINI_API_KEY
- LOG_LEVEL
- DATABASE_URL

No secrets must be stored in source code.

---

## 7. Natural Language to SQL Pipeline

The core workflow will not be a naive one-step prompt-to-SQL experience. Instead, it will use a structured pipeline that improves reliability and maintainability.

```text
User Question
  -> Conversation Context
  -> Intent Analyzer
  -> Schema Retriever
  -> Prompt Builder
  -> LLM
  -> SQL Validation
  -> Query Executor
  -> Result Formatter
  -> Frontend
```

### 7.1 Why the Pipeline Is Important

A single LLM call that directly generates SQL is brittle. A staged pipeline provides:

- better control over what context is provided
- more opportunities to validate and reject unsafe queries
- easier observability at each stage
- clearer test coverage for each component

### 7.2 Safety Rules

Only SELECT statements should be executable. The backend will reject:

- DELETE
- UPDATE
- INSERT
- DROP
- ALTER
- TRUNCATE

unless explicit future support is added.

### 7.3 Validation Layer

Validation will occur at two levels:

1. SQL syntax and dialect validation
2. Safety validation to ensure only read-only operations are executed

---

## 8. Conversation Memory and History

### 8.1 Design Choice

Conversation state will be stored separately from SQL execution history.

This is important because the application needs:

- conversational continuity for follow-up questions
- an audit trail of generated SQL and execution outcomes
- separate concerns for human-readable chat history and machine-auditable query history

### 8.2 Suggested Model Separation

- ConversationSession
  - session_id
  - created_at
  - updated_at
  - user_id (optional in v1)
- ChatMessage
  - id
  - session_id
  - role
  - content
  - created_at
- GeneratedQueryLog
  - id
  - session_id
  - sql
  - execution_time_ms
  - timestamp
  - status
  - error_message

This separation improves maintainability and reporting flexibility.

---

## 9. Frontend Architecture

### 9.1 User Experience Goals

The interface should feel like an internal enterprise analytics platform rather than a toy chatbot.

### 9.2 Main Views

- Chat view
  - streaming chat experience
  - markdown rendering
  - generated SQL display
  - execution time display
  - expandable reasoning metadata
  - table output
  - charts placeholder
- Database Connections view
  - create, edit, delete, test connection
- Settings view
  - select LLM provider
  - select database profile
  - temperature
  - max tokens
- Observability Dashboard
  - request count
  - average latency
  - SQL execution time
  - LLM response time
  - token usage
  - error rate
  - recent requests and SQL queries

### 9.2 State and Data Flow

The frontend will use:

- React + TypeScript
- Vite
- TailwindCSS
- React Query for server state
- React Router for navigation

This aligns well with enterprise UI patterns and keeps the UI responsive and testable.

---

## 10. API Design

The backend will expose a versioned REST API under /api/v1.

### 10.1 Proposed Endpoints

- POST /api/v1/chat
- POST /api/v1/database/connect
- GET /api/v1/database/schema
- GET /api/v1/database/tables
- POST /api/v1/query
- GET /api/v1/history
- GET /api/v1/metrics
- GET /api/v1/health

### 10.2 Design Rationale

A RESTful, versioned design is appropriate for enterprise internal tooling and allows future additions without breaking clients.

---

## 11. Observability and Monitoring

### 11.1 Logging

Structured logging will be used throughout the application.

Each request will receive a correlation ID.

Logs will include:

- incoming request metadata
- generated SQL
- execution duration
- LLM latency
- provider name
- database type
- error information

### 11.2 Metrics

The platform will collect basic operational metrics:

- request count
- average latency
- SQL execution time
- LLM response time
- token usage
- error rate

### 11.3 Why This Matters

Observability is essential for a platform that will eventually handle real business questions and production workloads. A system that cannot explain what happened during a request is not production-ready.

---

## 12. Error Handling Strategy

Errors will be handled centrally with a dedicated exception layer.

### 12.1 Design Principles

- No raw stack traces exposed in API responses
- Errors mapped to clear API error shapes
- Validation faults and provider faults handled distinctly
- Logging occurs at the boundary

### 12.2 Example Error Categories

- ValidationError
- ProviderError
- DatabaseConnectionError
- QuerySafetyError
- NotFoundError

This creates predictable behavior for clients and simplifies testing.

---

## 13. Configuration Management

Configuration will come exclusively from environment variables.

Required examples:

- OPENAI_API_KEY
- GEMINI_API_KEY
- DATABASE_URL
- LOG_LEVEL

### 13.1 Rationale

Environment-based configuration is standard in containerized and cloud-native systems. It prevents secrets from being checked into source control and makes deployment simpler.

---

## 14. Docker and Deployment

### 14.1 Services

The deployment topology will include:

- frontend service
- backend service
- PostgreSQL service
- Redis placeholder service

### 14.2 Why Docker Compose

Docker Compose provides a consistent local development and test environment and makes deployment easier to reason about.

### 14.3 Health Checks

Each service will expose health endpoints or health checks to support startup order and reliability.

---

## 15. Testing Strategy

### 15.1 Unit Tests

Unit tests will cover:

- prompt builders
- SQL validators
- connector factory behavior
- provider interface adapters
- service orchestration logic

### 15.2 Integration Tests

Integration tests will cover:

- API request flows
- database connector execution against ephemeral test databases
- LLM provider adapters using mocked responses

### 15.3 Testability Design Choice

The architecture intentionally favors dependency injection so tests can swap real providers for fakes or mocks without changing business logic.

---

## 16. Risks and Trade-Offs

### 16.1 Risks

- LLM-generated SQL may be unreliable without strong validation
- Database-specific SQL syntax variations may cause portability issues
- Provider APIs may change over time
- Prompt quality directly affects output correctness

### 16.2 Trade-Offs

- The staged pipeline is more complex than a single-prompt approach, but it is significantly more robust
- Interface-based design introduces more classes and indirection, but improves extensibility and testability
- Structured logging and metrics add operational overhead, but are necessary for production confidence

---

## 17. Recommended Implementation Phases

The project will be delivered in the following phases:

1. Phase 1: architecture and design approval
2. Phase 2: project skeleton
3. Phase 3: backend core
4. Phase 4: SQL provider layer
5. Phase 5: LLM provider layer
6. Phase 6: API layer
7. Phase 7: frontend
8. Phase 8: Docker
9. Phase 9: tests
10. Phase 10: production-readiness review and V2 recommendations

---

## 18. Final Recommendation

This architecture is intentionally designed to look and behave like a serious internal analytics platform rather than a demo application. The layered structure, provider abstraction, validation pipeline, and observability strategy all support long-term maintainability and scalable evolution.

If approved, the next step will be Phase 2: creating the project skeleton and initial structure.
