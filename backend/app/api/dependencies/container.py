from __future__ import annotations

from app.agents.langgraph_agent import LangGraphAgent
from app.core.config import settings
from app.domain.connection_profile import ConnectionProfile
from app.providers.llm.factory import LLMProviderFactory
from app.repositories.chat_history_repository import ChatHistoryRepository
from app.services.chat_service import ChatService
from app.services.connection_service import ConnectionProfileStore, ConnectorFactory
from app.services.prompt_builder import PromptBuilder
from app.services.query_executor import QueryExecutor
from app.services.schema_service import SchemaService
from app.services.sql_validator import SQLValidator

# Fixed id so ChatRequest.connection_id can default to this without a
# round trip to POST /api/v1/database/connect. Once that endpoint (and a
# real Database Connections view) exists, this becomes just one profile
# among many rather than the only one.
DEFAULT_SQLITE_CONNECTION_ID = "default-sqlite"


class Container:
    """Composition root.

    Previously LangGraphAgent instantiated LLMProviderFactory itself
    inside a node closure (`self.provider_factory = LLMProviderFactory()`
    in the old sql_builder node), which meant the graph owned both
    orchestration and infrastructure wiring. Now every shared dependency
    — the LLM provider factory, the connection profile store, the
    connector factory, and the new schema/validation/prompt/execution
    services — is built once here and injected into LangGraphAgent's
    constructor, so the graph only orchestrates.
    """

    def __init__(self) -> None:
        print("[backend] Initializing dependency container")

        self.history_repository = ChatHistoryRepository()
        print("[backend] ChatHistoryRepository created")

        self.llm_provider_factory = LLMProviderFactory()
        print("[backend] LLMProviderFactory created")

        self.connection_store = ConnectionProfileStore()
        self.connector_factory = ConnectorFactory()
        print("[backend] ConnectionProfileStore and ConnectorFactory created")

        self._seed_default_connection()

        self.schema_service = SchemaService(connector_factory=self.connector_factory)
        self.sql_validator = SQLValidator()
        self.prompt_builder = PromptBuilder()
        self.query_executor = QueryExecutor(connector_factory=self.connector_factory)
        print("[backend] SchemaService, SQLValidator, PromptBuilder, QueryExecutor created")

        self.agent = LangGraphAgent(
            llm_provider_factory=self.llm_provider_factory,
            connection_store=self.connection_store,
            schema_service=self.schema_service,
            prompt_builder=self.prompt_builder,
            sql_validator=self.sql_validator,
            query_executor=self.query_executor,
        )
        print("[backend] LangGraphAgent created with injected dependencies")

        self.chat_service = ChatService(
            agent=self.agent,
            history_repository=self.history_repository,
            provider_factory=self.llm_provider_factory,
            default_connection_id=DEFAULT_SQLITE_CONNECTION_ID,
        )
        print("[backend] ChatService created")

    def _seed_default_connection(self) -> None:
        """Register a default sqlite ConnectionProfile so a chat request
        with no connection_id still resolves to a real, queryable
        database via ConnectorFactory, instead of skipping schema
        retrieval and execution entirely.
        """
        profile = ConnectionProfile(
            id=DEFAULT_SQLITE_CONNECTION_ID,
            database_type="sqlite",
            database=settings.sqlite_path,
        )
        self.connection_store.create(profile)
        # Fail fast if the file/driver isn't usable, rather than silently
        # degrading every chat request to "no schema available".
        result = self.connector_factory.test_connection(profile)
        print(f"[backend] Default sqlite connection seeded: {result}")


container = Container()
