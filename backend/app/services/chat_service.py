from __future__ import annotations

from app.agents.langgraph_agent import LangGraphAgent
from app.api.schemas.chat import ChatRequest, ChatResponse
from app.core.config import settings
from app.core.logging import logger
from app.providers.llm.factory import LLMProviderFactory
from app.repositories.chat_history_repository import ChatHistoryRepository


class ChatService:
    """Thin orchestration entrypoint for chat requests.

    Previously ChatService ran the agent and then independently called
    `validate_select_statement` on the result, meaning SQL safety logic
    lived partly in the service layer and partly in the agent. Now that
    LangGraph owns generation, validation, execution, and formatting
    end-to-end (see langgraph_agent.py), ChatService's job shrinks to:
    load history, assemble the initial graph state, invoke the graph,
    persist the exchange, and translate the graph's formatted_response
    into a ChatResponse.

    NOTE: this also fixes `from venv import logger` (a no-op/incorrect
    import in the original file — the stdlib `venv` module has no
    `logger`) to use the app's actual structured logger, matching
    main.py's `from app.core.logging import logger`.
    """

    def __init__(
        self,
        agent: LangGraphAgent,
        history_repository: ChatHistoryRepository | None = None,
        provider_factory: LLMProviderFactory | None = None,
        default_connection_id: str | None = None,
    ) -> None:
        self.agent = agent
        self.history_repository = history_repository or ChatHistoryRepository()
        self.provider_factory = provider_factory or LLMProviderFactory()
        # Falls back to the container's seeded default sqlite connection
        # (see api/dependencies/container.py) so a request that doesn't
        # specify connection_id still gets schema-aware SQL generation
        # and real execution instead of silently skipping both.
        self.default_connection_id = default_connection_id
        print(f"[backend] ChatService initialized, default_connection_id={default_connection_id}")

    def handle_request(self, request: ChatRequest) -> ChatResponse:
        session_id = request.session_id or "session-1"
        connection_id = request.connection_id or self.default_connection_id
        print(f"[backend] ChatService.handle_request started for session {session_id}")
        logger.info("chat_request_started", extra={"session_id": session_id, "connection_id": connection_id})

        history = self._load_history_as_messages(session_id)

        self.history_repository.add_message(session_id, "user", request.question)
        print(f"[backend] User question stored: {request.question}")

        result = self.agent.run(
            question=request.question,
            connection_id=connection_id,
            provider=request.provider,
            conversation_history=history,
        )
        print(f"[backend] Agent run result: {result}")

        answer = result.get("answer", "")
        sql = result.get("sql")
        status = result.get("status", "ok")
        provider = result.get("provider") or settings.default_llm_provider

        self.history_repository.add_message(
            session_id,
            "assistant",
            answer,
            {"sql": sql, "status": status, "errors": result.get("errors", [])},
        )
        print(f"[backend] Assistant answer stored, status={status}")

        return ChatResponse(
            session_id=session_id,
            answer=answer,
            sql=sql,
            provider=provider,
            status=status,
            results=result.get("results"),
            metrics=result.get("metrics", {}),
            errors=result.get("errors", []),
        )

    def _load_history_as_messages(self, session_id: str) -> list[dict[str, str]]:
        """Best-effort conversion of stored history into the role/content
        message shape LangGraphAgent expects. If the repository doesn't
        expose a way to list prior messages, the graph simply runs
        without prior conversation context rather than failing.
        """
        get_messages = getattr(self.history_repository, "get_messages", None)
        if get_messages is None:
            return []
        try:
            stored = get_messages(session_id) or []
        except Exception as exc:
            print(f"[backend] Could not load history for session {session_id}: {exc}")
            return []
        return [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in stored]
