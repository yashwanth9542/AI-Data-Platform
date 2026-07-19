from __future__ import annotations

from typing import Optional


class PromptBuilder:
    """Builds the schema-aware, conversation-aware prompt sent to the LLM.

    Kept separate from LLMGenerationNode so prompt strategy can be
    iterated on and unit tested without touching graph wiring.
    """

    def build(self, question: str, schema: Optional[dict], conversation_context: str) -> str:
        schema_section = self._format_schema(schema)
        return f"""You are a SQL assistant. Translate the user's request into a single
safe, read-only SQL SELECT statement. Return ONLY the SQL query, with no
markdown, explanations, or code fences.

Conversation context:
{conversation_context or '(none)'}

Database schema:
{schema_section}

User request:
{question}
"""

    def _format_schema(self, schema: Optional[dict]) -> str:
        if not schema:
            return "(no schema available - no active connection)"
        lines = [f"dialect: {schema.get('dialect', 'unknown')}"]
        for table, columns in schema.get("tables", {}).items():
            lines.append(f"- {table}({', '.join(columns)})")
        return "\n".join(lines)
