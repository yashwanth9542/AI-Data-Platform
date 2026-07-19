from __future__ import annotations

from typing import Any, Optional

from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict

from app.core.config import settings
from app.providers.llm.factory import LLMProviderFactory
from app.services.connection_service import ConnectionNotFoundError, ConnectionProfileStore
from app.services.prompt_builder import PromptBuilder
from app.services.query_executor import QueryExecutor
from app.services.schema_service import SchemaService
from app.services.sql_validator import SQLValidator


class AgentState(TypedDict):
    # Input
    messages: list[dict[str, Any]]
    connection_id: Optional[str]
    provider: str

    # Working state, populated as the graph runs
    conversation_context: str
    connection_profile: Optional[dict[str, Any]]
    schema: Optional[dict[str, Any]]
    intent: str
    prompt: str
    raw_sql: Optional[str]
    validated_sql: Optional[str]
    execution_result: Optional[list[dict]]
    answer: str
    formatted_response: Optional[dict[str, Any]]
    metrics: dict[str, Any]
    errors: list[str]


class LangGraphAgent:
    """LangGraph is the single orchestration layer for a chat request.

    Previously this class wrapped a two-node graph (intent_analyzer ->
    sql_builder) where sql_builder instantiated an LLM provider directly
    and generated SQL in one shot. That made the graph a thin wrapper
    around a single LLM call rather than a real orchestration engine.

    Now the graph owns the full pipeline described in
    docs/architecture/phase1-architecture-design.md section 7: intent
    detection, schema retrieval, prompt construction, SQL generation,
    validation, execution, and response formatting are each their own
    node. Nodes have one responsibility each and are independently
    testable. All infrastructure dependencies are injected through the
    constructor rather than instantiated inside node closures, so tests
    can substitute fakes without touching graph wiring.

    ChatService (see app/services/chat_service.py) stays thin: it
    assembles the initial state and invokes this graph. It no longer
    calls the SQL validator itself.
    """

    def __init__(
        self,
        llm_provider_factory: LLMProviderFactory,
        connection_store: ConnectionProfileStore,
        schema_service: SchemaService,
        prompt_builder: PromptBuilder,
        sql_validator: SQLValidator,
        query_executor: QueryExecutor,
    ) -> None:
        self.llm_provider_factory = llm_provider_factory
        self.connection_store = connection_store
        self.schema_service = schema_service
        self.prompt_builder = prompt_builder
        self.sql_validator = sql_validator
        self.query_executor = query_executor
        self.workflow = self._build_workflow()

    # ------------------------------------------------------------------
    # Node implementations
    # ------------------------------------------------------------------

    def _conversation_context_node(self, state: AgentState) -> AgentState:
        history = state["messages"][:-1]
        context = "\n".join(f"{m.get('role', 'user')}: {m.get('content', '')}" for m in history)
        print(f"[backend] ConversationContextNode built context with {len(history)} prior messages")
        return {**state, "conversation_context": context}

    def _intent_analysis_node(self, state: AgentState) -> AgentState:
        question = state["messages"][-1]["content"] if state["messages"] else ""
        intent = "data_exploration" if "sales" in question.lower() else "general"
        print(f"[backend] IntentAnalysisNode detected intent={intent} for question={question!r}")
        return {**state, "intent": intent}

    def _schema_retrieval_node(self, state: AgentState) -> AgentState:
        errors = list(state.get("errors", []))
        schema: Optional[dict[str, Any]] = None
        profile_dict: Optional[dict[str, Any]] = None

        connection_id = state.get("connection_id")
        if connection_id:
            try:
                profile = self.connection_store.get(connection_id)
                schema = self.schema_service.get_schema(profile)
                profile_dict = vars(profile)
            except ConnectionNotFoundError as exc:
                print(f"[backend] SchemaRetrievalNode connection not found: {exc}")
                errors.append(str(exc))
            except Exception as exc:  # connector-level failures shouldn't crash the graph
                print(f"[backend] SchemaRetrievalNode failed to fetch schema: {exc}")
                errors.append(f"Schema retrieval failed: {exc}")
        else:
            print("[backend] SchemaRetrievalNode skipped: no connection_id provided")

        return {**state, "schema": schema, "connection_profile": profile_dict, "errors": errors}

    def _prompt_builder_node(self, state: AgentState) -> AgentState:
        question = state["messages"][-1]["content"] if state["messages"] else ""
        prompt = self.prompt_builder.build(
            question=question,
            schema=state.get("schema"),
            conversation_context=state.get("conversation_context", ""),
        )
        print(f"[backend] PromptBuilderNode built prompt ({len(prompt)} chars)")
        return {**state, "prompt": prompt}
    
    def _llm_generation_node(self, state: AgentState) -> AgentState:
        errors = list(state.get("errors", []))
        raw_sql = None
        try:
            provider = self.llm_provider_factory.create(state.get("provider"))
            print(f"[backend] LLMGenerationNode using provider: {state.get('provider')}")
            # raw_sql = (
            #     provider.generate(state["prompt"])
            #     .replace("```sql", "")
            #     .replace("```", "")
            #     .strip()
            # )
# For testing, we can simulate a raw SQL response
            raw_sql = "SELECT name FROM sqlite_schema WHERE type = 'table' AND name NOT LIKE 'sqlite_%';"
            print(f"[backend] LLMGenerationNode produced SQL: {raw_sql}")
        except Exception as exc:
            print(f"[backend] LLMGenerationNode failed: {exc}")
            errors.append(f"LLM generation failed: {exc}")
        return {**state, "raw_sql": raw_sql, "errors": errors}

    def _sql_validation_node(self, state: AgentState) -> AgentState:
        errors = list(state.get("errors", []))
        raw_sql = state.get("raw_sql")
        validated_sql = None

        if not raw_sql:
            errors.append("No SQL was generated to validate")
        else:
            is_valid, validation_errors = self.sql_validator.validate(raw_sql)
            if is_valid:
                validated_sql = raw_sql
            else:
                errors.extend(validation_errors)

        print(f"[backend] SQLValidationNode validated_sql={validated_sql!r} errors={errors}")
        return {**state, "validated_sql": validated_sql, "errors": errors}

    def _sql_execution_node(self, state: AgentState) -> AgentState:
        errors = list(state.get("errors", []))
        execution_result = None
        metrics = dict(state.get("metrics", {}))

        connection_id = state.get("connection_id")
        validated_sql = state.get("validated_sql")

        if not connection_id:
            errors.append("SQL was validated but no connection_id was provided; execution skipped")
        else:
            try:
                profile = self.connection_store.get(connection_id)
                execution_result, elapsed_ms = self.query_executor.execute(profile, validated_sql)
                metrics["sql_execution_time_ms"] = elapsed_ms
            except Exception as exc:
                print(f"[backend] SQLExecutionNode failed: {exc}")
                errors.append(f"Query execution failed: {exc}")

        return {**state, "execution_result": execution_result, "metrics": metrics, "errors": errors}

    def _response_formatter_node(self, state: AgentState) -> AgentState:
        errors = state.get("errors", [])
        raw_sql = state.get("raw_sql")
        validated_sql = state.get("validated_sql")

        if state.get("execution_result") is not None:
            answer = f"Ran the generated SQL and found {len(state['execution_result'])} row(s)."
            answer += f"results={state['execution_result']}"  # For debugging; in production, consider summarizing or truncating
            status = "ok"
        elif validated_sql:
            answer = "Generated a valid, read-only SQL query."
            status = "ok"
        elif raw_sql and not validated_sql:
            # SQL was generated but rejected by SQLValidationNode (see
            # phase1-architecture-design.md section 7.2 safety rules).
            answer = "The generated query was rejected because it is not a read-only SELECT statement."
            status = "blocked"
        else:
            answer = f"Could not complete the request: {'; '.join(errors)}" if errors else "No SQL could be generated for this request."
            status = "error"

        formatted_response = {
            "answer": answer,
            "status": status,
            "intent": state.get("intent"),
            "sql": validated_sql,
            "provider": state.get("provider", settings.default_llm_provider),
            "results": state.get("execution_result"),
            "metrics": state.get("metrics", {}),
            "errors": errors,
        }
        print(f"[backend] ResponseFormatterNode built response: {formatted_response}")
        return {**state, "answer": answer, "formatted_response": formatted_response}

    # ------------------------------------------------------------------
    # Graph wiring
    # ------------------------------------------------------------------

    def _route_after_validation(self, state: AgentState) -> str:
        return "sql_execution" if state.get("validated_sql") else "response_formatter"

    def _build_workflow(self) -> StateGraph:
        builder = StateGraph(AgentState)

        builder.add_node("build_conversation_context", self._conversation_context_node)
        builder.add_node("intent_analysis", self._intent_analysis_node)
        builder.add_node("schema_retrieval", self._schema_retrieval_node)
        builder.add_node("prompt_builder", self._prompt_builder_node)
        builder.add_node("llm_generation", self._llm_generation_node)
        builder.add_node("sql_validation", self._sql_validation_node)
        builder.add_node("sql_execution", self._sql_execution_node)
        builder.add_node("response_formatter", self._response_formatter_node)

        builder.set_entry_point("build_conversation_context")
        builder.add_edge("build_conversation_context", "intent_analysis")
        builder.add_edge("intent_analysis", "schema_retrieval")
        builder.add_edge("schema_retrieval", "prompt_builder")
        builder.add_edge("prompt_builder", "llm_generation")
        builder.add_edge("llm_generation", "sql_validation")
        builder.add_conditional_edges(
            "sql_validation",
            self._route_after_validation,
            {
                "sql_execution": "sql_execution",
                "response_formatter": "response_formatter",
            },
        )
        builder.add_edge("sql_execution", "response_formatter")
        builder.add_edge("response_formatter", END)

        return builder.compile()

    # ------------------------------------------------------------------
    # Public entrypoint
    # ------------------------------------------------------------------

    def run(
        self,
        question: str,
        connection_id: Optional[str] = None,
        provider: Optional[str] = None,
        conversation_history: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        print(f"[backend] LangGraphAgent.run started for question={question!r} connection_id={connection_id}")
        messages = list(conversation_history or []) + [{"role": "user", "content": question}]
        initial_state: AgentState = {
            "messages": messages,
            "connection_id": connection_id,
            "provider": provider or settings.default_llm_provider,
            "conversation_context": "",
            "connection_profile": None,
            "schema": None,
            "intent": "",
            "prompt": "",
            "raw_sql": None,
            "validated_sql": None,
            "execution_result": None,
            "answer": "",
            "formatted_response": None,
            "metrics": {},
            "errors": [],
        }
        result = self.workflow.invoke(initial_state)
        print(f"[backend] LangGraphAgent.run result: {result}")
        return result.get("formatted_response") or {
            "answer": result.get("answer", ""),
            "status": "error",
            "sql": result.get("validated_sql"),
            "provider": result.get("provider", settings.default_llm_provider),
            "results": result.get("execution_result"),
            "metrics": result.get("metrics", {}),
            "errors": result.get("errors", []),
        }
