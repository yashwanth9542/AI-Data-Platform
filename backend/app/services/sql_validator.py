from __future__ import annotations

import re

_UNSAFE_KEYWORDS = ("DELETE", "UPDATE", "INSERT", "DROP", "ALTER", "TRUNCATE")


class SQLValidator:
    """Enforces the read-only safety rules from
    docs/architecture/phase1-architecture-design.md sections 7.2-7.3:
    only SELECT statements may execute, and DML/DDL keywords are rejected
    outright rather than sanitized.

    Used by SQLValidationNode inside the LangGraph workflow so validation
    happens as its own graph stage instead of being bolted onto
    ChatService (previously ChatService called `validate_select_statement`
    directly after the agent returned).
    """

    def validate(self, sql: str) -> tuple[bool, list[str]]:
        errors: list[str] = []
        if not sql or not sql.strip():
            return False, ["Empty SQL statement"]

        normalized = sql.strip().rstrip(";")
        first_token = normalized.split(None, 1)[0].upper() if normalized else ""

        if first_token != "SELECT":
            errors.append(f"Only SELECT statements are allowed, got: {first_token or 'EMPTY'}")

        for keyword in _UNSAFE_KEYWORDS:
            if re.search(rf"\b{keyword}\b", normalized, flags=re.IGNORECASE):
                errors.append(f"Unsafe keyword detected: {keyword}")

        if ";" in normalized:
            errors.append("Multiple statements are not allowed")

        is_valid = not errors
        print(f"[backend] SQLValidator.validate sql={normalized!r} valid={is_valid} errors={errors}")
        return is_valid, errors


def validate_select_statement(sql: str) -> bool:
    """Backward-compatible function wrapper.

    Kept so any existing call sites (e.g. the pre-refactor ChatService,
    which imported `validate_select_statement` directly) continue to
    work. New code should use SQLValidator via the graph instead.
    """
    is_valid, _errors = SQLValidator().validate(sql)
    return is_valid
