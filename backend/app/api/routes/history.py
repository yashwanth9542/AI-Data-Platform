from fastapi import APIRouter, Depends

from app.api.dependencies.container import container
from app.repositories.chat_history_repository import ChatHistoryRepository

router = APIRouter(prefix="/history", tags=["history"])


def get_history_repository() -> ChatHistoryRepository:
    print("[backend] Injecting ChatHistoryRepository from container")
    return container.history_repository


@router.get("")
def history(session_id: str | None = None, repository: ChatHistoryRepository = Depends(get_history_repository)) -> dict:
    print(f"[backend] /history called with session_id: {session_id}")
    if session_id:
        history_data = repository.get_session(session_id)
        print(f"[backend] Retrieved history for session {session_id}")
        return {"session_id": session_id, "history": history_data}
    all_sessions = repository.get_all_sessions()
    print(f"[backend] Retrieved all sessions: {len(all_sessions)}")
    return {"sessions": all_sessions}
