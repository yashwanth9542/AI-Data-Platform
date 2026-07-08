# Copilot Instructions for AI Data Platform

This repository is a simple multi-service app with:
- React frontend in `frontend/`
- FastAPI backend in `backend/`
- Docker compose orchestration in `docker-compose.yml`

## Primary areas of focus
- Backend service entrypoint: `backend/app/main.py`
- Chat API: `backend/app/api/routes/chat.py`
- Dependency wiring: `backend/app/api/dependencies/container.py`
- Chat orchestration: `backend/app/services/chat_service.py`
- Agent workflow: `backend/app/agents/langgraph_agent.py`
- Provider abstractions: `backend/app/providers/database/` and `backend/app/providers/llm/`

## Guidance for code changes
- Keep HTTP route handlers thin; business logic belongs in services or agents.
- Preserve the provider-based design when adding new database or LLM integrations.
- Use `from app...` imports in backend code because `PYTHONPATH=/app/backend` is expected in Docker and local startup.
- Prefer linking to `README.md` and `docs/architecture/phase1-architecture-design.md` rather than duplicating architecture details.

## Common tasks
- To run the backend locally:
  - `cd backend`
  - `python -m venv .venv`
  - `.venv\Scripts\activate` (Windows)
  - `pip install -r requirements.txt`
  - `uvicorn app.main:app --reload`
- To run the frontend locally:
  - `cd frontend`
  - `npm install`
  - `npm run dev`
- To run both via Docker:
  - `docker compose up --build`

## Notes
- There is no dedicated tests folder currently present in this workspace.
- The current LangGraph agent implementation is a simple state graph used for intent and SQL construction; extend it carefully.
