# Handoff for Next Coding Agent

## Project Summary
AI Data Platform is a starter implementation of an internal analytics copilot. The current version focuses on establishing the project structure and demonstrating a LangGraph-based orchestration flow for a natural-language-to-SQL experience.

## Current Status
The repository now contains:
- a FastAPI backend with chat, history, database, and metrics routes
- a React + Vite frontend with a functional chat UI and database connection/query controls
- a LangGraph-based workflow that produces an intent and SQL draft
- configuration-driven LLM provider support for OpenAI and Gemini
- database connector abstractions for SQLite, PostgreSQL, and MySQL
- a real MySQL connector path that uses mysql-connector-python when available for connection checks, schema inspection, and query execution
- SQLite-backed chat history persistence
- structured logging and centralized error handling
- Docker and Compose configuration

The implementation is now much closer to the intended architecture, although live execution is still dependent on valid environment configuration and driver availability.

## Repository Structure

```text
SQL-Agent/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   └── langgraph_agent.py
│   │   ├── api/
│   │   │   ├── dependencies/
│   │   │   │   └── container.py
│   │   │   ├── routes/
│   │   │   │   ├── chat.py
│   │   │   │   └── health.py
│   │   │   └── schemas/
│   │   │       └── chat.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── providers/
│   │   │   ├── database/
│   │   │   │   ├── base.py
│   │   │   │   ├── mysql.py
│   │   │   │   ├── postgres.py
│   │   │   │   └── sqlite.py
│   │   │   └── llm/
│   │   │       ├── base.py
│   │   │       ├── gemini.py
│   │   │       └── openai.py
│   │   ├── services/
│   │   │   ├── chat_service.py
│   │   │   └── connection_service.py
│   │   ├── main.py
│   │   └── __init__.py
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── styles.css
│   ├── package.json
│   ├── vite.config.ts
│   └── index.html
├── docs/
├── Dockerfile
├── docker-compose.yml
├── README.md
└── handoff.md
```

## Backend Notes
### Current implementation
- FastAPI app is bootstrapped in [backend/app/main.py](backend/app/main.py)
- A basic chat endpoint exists at `/api/v1/chat`
- A health endpoint exists at `/api/v1/health`
- A LangGraph workflow is implemented in [backend/app/agents/langgraph_agent.py](backend/app/agents/langgraph_agent.py)
- The workflow currently acts as a simple two-step placeholder:
  1. intent analysis
  2. SQL draft generation

### Important implementation details
- The backend is structured around a service layer and provider abstractions.
- The app uses dependency injection style via a lightweight container in [backend/app/api/dependencies/container.py](backend/app/api/dependencies/container.py).
- LLM and database providers are defined as abstract interfaces with concrete starter implementations.

### Gaps to address next
- add provider-specific SDK integration tests for OpenAI and Gemini beyond the current HTTP-based approach
- add real execution against live PostgreSQL and SQLite backends, not just MySQL
- add authentication and authorization for internal use
- add API tests and integration tests for provider and connector flows
- add request correlation IDs and richer metrics collection
- improve frontend state management and form validation for connection settings

## Frontend Notes
### Current implementation
- A minimal Vite + React app exists in [frontend/src/App.tsx](frontend/src/App.tsx)
- The app includes navigation placeholders for Chat and Connections
- The UI is still a shell and does not yet communicate with the backend

### Gaps to address next
- chat UI wired to the backend API
- database connection management UI
- loading/error states
- styling and component structure

## Environment and Setup
### Backend
From the repository root:
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # on Windows PowerShell
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Docker
```bash
docker compose up --build
```

## Recommended Next Work
The highest-value next steps are:
1. Implement chat history persistence
2. Add real connection management endpoints and schema inspection
3. Replace the placeholder LangGraph workflow with a more realistic SQL generation pipeline
4. Connect the frontend chat UI to the backend API
5. Add tests for the backend workflow and provider abstractions

## Notes for the Next Agent
- This is a foundation project, not a completed product.
- Prefer improving the architecture rather than patching around incomplete behaviors.
- Keep new work aligned with the original design goals:
  - modularity
  - extensibility
  - testability
  - observability
- Avoid hardcoding database or LLM provider logic into route handlers.
