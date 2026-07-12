from app.agents.langgraph_agent import LangGraphAgent
from app.repositories.sqlite_chat_history_repository import SQLiteChatHistoryRepository
from app.services.chat_service import ChatService
from app.services.connection_service import ConnectorFactory


class Container:
    def __init__(self) -> None:
        print("[backend] Initializing dependency container")
        self.history_repository = SQLiteChatHistoryRepository()
        print("[backend] SQLiteChatHistoryRepository created")
        self.connector_factory = ConnectorFactory()
        print("[backend] ConnectorFactory created")
        self.chat_service = ChatService(agent=LangGraphAgent(), history_repository=self.history_repository)
        print("[backend] ChatService created")


container = Container()
