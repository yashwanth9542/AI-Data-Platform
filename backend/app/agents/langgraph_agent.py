from __future__ import annotations

from typing import Any

from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict


class AgentState(TypedDict):
    messages: list[dict[str, Any]]
    answer: str
    sql: str | None
    provider: str


class LangGraphAgent:
    def __init__(self) -> None:
        print("[backend] LangGraphAgent initializing")
        self.workflow = self._build_workflow()
        print("[backend] LangGraphAgent workflow built")

    def _build_workflow(self) -> StateGraph:
        def intent_analyzer(state: AgentState) -> AgentState:
            question = state["messages"][-1]["content"] if state["messages"] else ""
            intent = "data_exploration" if "sales" in question.lower() else "general"
            print(f"[backend] Agent intent_analyzer running for question: {question}")
            return {
                "messages": state["messages"],
                "answer": f"Intent detected: {intent}",
                "sql": None,
                "provider": "openai",
            }

        def sql_builder(state: AgentState) -> AgentState:
            question = state["messages"][-1]["content"] if state["messages"] else ""
            print(f"[backend] Agent sql_builder generating SQL for question: {question}")
            sql = f"SELECT * FROM analytics_sample WHERE question LIKE '%{question}%';"
            return {
                "messages": state["messages"],
                "answer": state["answer"],
                "sql": sql,
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
            "provider": "openai",
        }
        result = self.workflow.invoke(initial_state)
        print(f"[backend] LangGraphAgent.run result: {result}")
        return {
            "answer": result.get("answer", ""),
            "sql": result.get("sql"),
            "provider": result.get("provider", "openai"),
        }
