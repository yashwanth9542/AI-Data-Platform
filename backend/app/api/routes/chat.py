from fastapi import APIRouter, Depends

from app.api.schemas.chat import ChatRequest, ChatResponse
from app.api.dependencies.container import container
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


def get_chat_service() -> ChatService:
    print("[backend] Injecting ChatService from container")
    return container.chat_service


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, service: ChatService = Depends(get_chat_service)) -> ChatResponse:
    print(f"[backend] /chat endpoint called with question: {request.question}")
    response = service.handle_request(request)
    print(f"[backend] /chat endpoint returning response status: {response.status}")
    return response
