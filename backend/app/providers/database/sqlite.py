from pathlib import Path

from app.core.config import settings
from app.providers.database.base import DatabaseConnector


class SQLiteConnector(DatabaseConnector):
    def __init__(self, path: str | None = None) -> None:
        self.path = Path(path or settings.sqlite_path)
        self.connected = False

    def connect(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connected = True

    def validate_connection(self) -> bool:
        self.connect()
        return self.path.exists() or self.connected

    def execute_query(self, query: str) -> list[dict]:
        self.connect()
        return [{"query": query, "result": "sqlite-placeholder"}]

    def inspect_schema(self) -> dict:
        self.connect()
        return {"dialect": "sqlite", "path": str(self.path)}

    def list_tables(self) -> list[str]:
        self.connect()
        return ["analytics_sample"]

    def list_columns(self, table_name: str) -> list[str]:
        self.connect()
        return ["id", "name", "value"] if table_name else []
