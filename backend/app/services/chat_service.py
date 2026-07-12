from app.api.schemas.chat import ChatRequest, ChatResponse
from app.agents.langgraph_agent import LangGraphAgent
from app.core.config import settings
from app.providers.llm.factory import LLMProviderFactory
from app.repositories.chat_history_repository import ChatHistoryRepository
from app.services.sql_validator import validate_select_statement


class ChatService:
    def __init__(self, agent: LangGraphAgent, history_repository: ChatHistoryRepository | None = None, provider_factory: LLMProviderFactory | None = None) -> None:
        self.agent = agent
        self.history_repository = history_repository or ChatHistoryRepository()
        self.provider_factory = provider_factory or LLMProviderFactory()
        print("[backend] ChatService initialized")

    def handle_request(self, request: ChatRequest) -> ChatResponse:
        session_id = request.session_id or "session-1"
        print(f"[backend] ChatService.handle_request started for session {session_id}")
        self.history_repository.add_message(session_id, "user", request.question)
        print(f"[backend] User question stored: {request.question}")

        provider = self.provider_factory.create(settings.default_llm_provider)
        print(f"[backend] Using provider: {settings.default_llm_provider}")
        prompt = f"Translate the request into a safe analytic query: {request.question}"
        print(f"[backend] Provider prompt: {prompt}")
        provider_response = provider.generate(prompt)
        print(f"[backend] Provider response received")

        result = self.agent.run(request.question)
        print(f"[backend] Agent run result: {result}")
        sql = result.get("sql")
        is_safe = sql is None or validate_select_statement(sql)
        print(f"[backend] SQL extracted: {sql}, safe: {is_safe}")

        if sql and not is_safe:
            response_text = "The generated query was rejected because it is not a read-only SELECT statement."
            self.history_repository.add_message(session_id, "assistant", response_text, {"blocked": True})
            print("[backend] Blocked unsafe SQL query")
            return ChatResponse(session_id=session_id, answer=response_text, sql=None, provider=settings.default_llm_provider, status="blocked")

        response_text = f"{result.get('answer', '')} | {provider_response}"
        self.history_repository.add_message(session_id, "assistant", response_text, {"sql": sql})
        print("[backend] Assistant answer stored and response ready")
        return ChatResponse(
            session_id=session_id,
            answer=response_text,
            sql=sql,
            provider=settings.default_llm_provider,
            status="ok",
        )
