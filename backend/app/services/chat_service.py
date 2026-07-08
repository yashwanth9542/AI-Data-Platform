from app.api.schemas.chat import ChatRequest, ChatResponse
from app.agents.langgraph_agent import LangGraphAgent


class ChatService:
    def __init__(self, agent: LangGraphAgent) -> None:
        self.agent = agent

    def handle_request(self, request: ChatRequest) -> ChatResponse:
        result = self.agent.run(request.question)
        return ChatResponse(
            session_id=request.session_id or "session-1",
            answer=result["answer"],
            sql=result.get("sql"),
            provider=result.get("provider", "openai"),
            status="ok",
        )
