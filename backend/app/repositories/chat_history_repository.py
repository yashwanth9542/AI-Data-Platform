import json
from pathlib import Path
from typing import Any
from uuid import uuid4


class ChatHistoryRepository:
    def __init__(self, storage_path: str | None = None) -> None:
        self.storage_path = Path(storage_path or "app/data/chat_history.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.write_text("{}", encoding="utf-8")

    def _load(self) -> dict[str, Any]:
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def _save(self, payload: dict[str, Any]) -> None:
        self.storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def ensure_session(self, session_id: str) -> None:
        data = self._load()
        data.setdefault(session_id, {"messages": []})
        self._save(data)

    def add_message(self, session_id: str, role: str, content: str, metadata: dict[str, Any] | None = None) -> None:
        self.ensure_session(session_id)
        data = self._load()
        entry = {"id": str(uuid4()), "role": role, "content": content, "metadata": metadata or {}}
        data[session_id]["messages"].append(entry)
        self._save(data)

    def get_session(self, session_id: str) -> dict[str, Any]:
        data = self._load()
        return data.get(session_id, {"messages": []})

    def get_all_sessions(self) -> list[dict[str, Any]]:
        data = self._load()
        return [{"session_id": session_id, **payload} for session_id, payload in data.items()]
