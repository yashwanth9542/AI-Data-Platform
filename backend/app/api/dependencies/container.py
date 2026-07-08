from app.services.chat_service import ChatService
from app.agents.langgraph_agent import LangGraphAgent


class Container:
    def __init__(self) -> None:
        self.chat_service = ChatService(agent=LangGraphAgent())


container = Container()
