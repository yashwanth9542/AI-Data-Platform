from __future__ import annotations

from typing import Any

from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict
from app.core.config import settings
from app.providers.llm.factory import LLMProviderFactory

class AgentState(TypedDict):
    messages: list[dict[str, Any]]
    answer: str
    sql: str | None
    provider: str


class LangGraphAgent:

    def __init__(self):
        self.provider_factory = LLMProviderFactory()
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        def intent_analyzer(state: AgentState) -> AgentState:
            question = state["messages"][-1]["content"] if state["messages"] else ""
            intent = "data_exploration" if "sales" in question.lower() else "general"
            print(f"[backend] Agent intent_analyzer running for question: {question}")
            return {
                "messages": state["messages"],
                "answer": f"Intent detected: {intent}",
                "sql": None,
                "provider": settings.default_llm_provider
            }

        def sql_builder(state: AgentState) -> AgentState:
            question = state["messages"][-1]["content"] if state["messages"] else ""
            print(f"[backend] Agent sql_builder generating SQL for question: {question}")
            # sql = f"SELECT * FROM analytics_sample WHERE question LIKE '%{question}%';"
            
            provider = self.provider_factory.create(settings.default_llm_provider)
            print(f"[backend] Using provider: {settings.default_llm_provider}")
            prompt = f"""Translate the following request into a safe read-only SQL SELECT statement.
                        User request:
                        {question}
                        output the SQL query only, no explanations or markdown formatting."""
            print(f"[backend] Provider prompt: {prompt}")
            provider_response = (
                                provider.generate(prompt)
                                .replace("```sql", "")
                                .replace("```", "")
                                .strip()
                            )
            
            return {
                "messages": state["messages"],
                "answer": state["answer"],
                "sql": provider_response,
                "provider": state["provider"],
            }

        builder = StateGraph(AgentState)
        builder.add_node("intent_analyzer", intent_analyzer)
        builder.add_node("sql_builder", sql_builder)
        builder.set_entry_point("intent_analyzer")
        builder.add_edge("intent_analyzer", "sql_builder")
        builder.add_edge("sql_builder", END)
        return builder.compile()

    def run(self, question: str) -> dict[str, Any]:
        print(f"[backend] LangGraphAgent.run started for question: {question}")
        initial_state: AgentState = {
            "messages": [{"role": "user", "content": question}],
            "answer": "",
            "sql": None,
            "provider": settings.default_llm_provider,
        }
        result = self.workflow.invoke(initial_state)
        print(f"[backend] LangGraphAgent.run result: {result}")
        return {
            "answer": result.get("answer", ""),
            "sql": result.get("sql"),
            "provider": result.get("provider", "openai"),
        }
