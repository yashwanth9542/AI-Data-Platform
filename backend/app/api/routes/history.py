from fastapi import APIRouter, Depends

from app.api.dependencies.container import container
from app.repositories.chat_history_repository import ChatHistoryRepository

router = APIRouter(prefix="/history", tags=["history"])


def get_history_repository() -> ChatHistoryRepository:
    return container.history_repository


@router.get("")
def history(session_id: str | None = None, repository: ChatHistoryRepository = Depends(get_history_repository)) -> dict:
    if session_id:
        return {"session_id": session_id, "history": repository.get_session(session_id)}
    return {"sessions": repository.get_all_sessions()}
