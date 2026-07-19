from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    question: str
    # New: lets the graph retrieve the active ConnectionProfile for
    # schema-aware SQL generation and execution (see SchemaRetrievalNode /
    # SQLExecutionNode in langgraph_agent.py).
    connection_id: Optional[str] = None
    provider: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sql: Optional[str] = None
    provider: str
    status: str
    # New: surfaced from the graph's ResponseFormatterNode. Optional /
    # defaulted so existing frontend code that only reads
    # session_id/answer/sql/provider/status keeps working unchanged.
    results: Optional[list[dict[str, Any]]] = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
