import sqlite3
from pathlib import Path
from typing import Any


class SQLiteChatHistoryRepository:
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = Path(db_path or "./data/chat_history.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _initialize(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                )
                """
            )
            connection.commit()

    def ensure_session(self, session_id: str) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("INSERT OR IGNORE INTO sessions (session_id) VALUES (?)", (session_id,))
            connection.commit()

    def add_message(self, session_id: str, role: str, content: str, metadata: dict[str, Any] | None = None) -> None:
        self.ensure_session(session_id)
        metadata_text = repr(metadata or {})
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                "INSERT INTO messages (id, session_id, role, content, metadata) VALUES (?, ?, ?, ?, ?)",
                (self._new_id(), session_id, role, content, metadata_text),
            )
            connection.commit()

    def get_session(self, session_id: str) -> dict[str, Any]:
        with sqlite3.connect(self.db_path) as connection:
            rows = connection.execute(
                "SELECT role, content, metadata FROM messages WHERE session_id = ? ORDER BY created_at ASC",
                (session_id,),
            ).fetchall()
        return {
            "session_id": session_id,
            "messages": [
                {"role": role, "content": content, "metadata": eval(metadata)} for role, content, metadata in rows
            ],
        }

    def get_all_sessions(self) -> list[dict[str, Any]]:
        with sqlite3.connect(self.db_path) as connection:
            rows = connection.execute("SELECT session_id FROM sessions ORDER BY created_at ASC").fetchall()
        return [{"session_id": session_id} for (session_id,) in rows]

    def _new_id(self) -> str:
        import uuid
        return str(uuid.uuid4())
