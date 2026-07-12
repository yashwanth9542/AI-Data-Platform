# AI Data Platform Agent Guide

## Purpose
This file helps AI coding agents understand the repository structure, architecture, and common conventions so they can be productive quickly.

## What this project is
- A local web application with a React frontend and FastAPI backend.
- The backend is the core orchestration layer that handles user chat requests, builds SQL, and routes work through provider abstractions.
- Docker Compose is provided for local development and running frontend/backend together.

## Key startup commands
- Backend:
  - `cd backend`
  - `python -m venv .venv`
  - `source .venv/bin/activate` (Windows: `.venv\\Scripts\\activate`)
  - `pip install -r requirements.txt`
  - `uvicorn app.main:app --reload`
- Frontend:
  - `cd frontend`
  - `npm install`
  - `npm run dev`
- Docker:
  - `docker compose up --build`

## Important files and directories
- `backend/app/main.py`
  - FastAPI app entrypoint and router registration.
- `backend/app/api/routes/chat.py`
  - Chat HTTP endpoint and FastAPI dependency wiring.
- `backend/app/api/dependencies/container.py`
  - Simple dependency container that constructs `ChatService` and `LangGraphAgent`.
- `backend/app/services/chat_service.py`
  - Orchestrates chat requests and calls the agent.
- `backend/app/agents/langgraph_agent.py`
  - Encodes the current LangGraph-based workflow for intent detection and SQL generation.
- `backend/app/providers/database/`
  - Database connector abstractions and implementations.
- `backend/app/providers/llm/`
  - LLM provider abstractions and implementations.
- `frontend/`
  - Vite + React TypeScript app.

## Architecture patterns and conventions
- The backend uses a provider-based abstraction layer for databases and LLMs.
- The chat flow is implemented as a service layer calling an agent implementation.
- Dependency injection is minimal but centralized in `backend/app/api/dependencies/container.py`.
- Package imports use `from app...` because the Docker container sets `PYTHONPATH=/app/backend`.
- New backend components should follow the existing separation of:
  - `api` for HTTP routes and request/response models
  - `services` for orchestration/business logic
  - `agents` for workflow/agent behavior
  - `providers` for pluggable infrastructure connectors

## Useful documentation
- `README.md` — quick start and architecture overview.
- `docs/architecture/phase1-architecture-design.md` — detailed backend architecture, provider design, and future test structure.

## Agent guidance
- Prefer linking to existing docs instead of duplicating them.
- When modifying backend behavior, preserve the provider-based design and keep application logic out of API route handlers.
- When adding a new database or LLM provider, implement the corresponding base interface and wire it through the container.
- No dedicated test suite exists in the current workspace, so be conservative and explicit when proposing tests or structure changes.
