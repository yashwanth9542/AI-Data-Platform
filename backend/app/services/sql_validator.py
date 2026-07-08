import re


def validate_select_statement(query: str) -> bool:
    normalized = query.strip().upper()
    if not normalized.startswith("SELECT"):
        return False

    forbidden_keywords = [
        "DELETE",
        "UPDATE",
        "INSERT",
        "DROP",
        "ALTER",
        "TRUNCATE",
    ]

    if any(keyword in normalized for keyword in forbidden_keywords):
        return False

    return bool(re.search(r"\bFROM\b", normalized))
