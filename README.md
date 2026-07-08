# AI Data Platform

AI Data Platform is an internal analytics copilot that translates natural language into SQL and executes it against multiple SQL databases.

## Architecture

- React frontend
- FastAPI backend
- LangGraph-based workflow orchestration
- Provider-based design for databases and LLMs

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows use .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker Compose

```bash
docker compose up --build
```
