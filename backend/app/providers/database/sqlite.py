from pathlib import Path

from app.core.config import settings
from app.providers.database.base import DatabaseConnector


class SQLiteConnector(DatabaseConnector):
    def __init__(self, path: str | None = None) -> None:
        self.path = Path(path or settings.sqlite_path)
        self.connected = False
        print(f"[backend] SQLiteConnector initialized with path: {self.path}")

    def connect(self) -> None:
        print(f"[backend] SQLiteConnector.connect called")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connected = True

    def validate_connection(self) -> bool:
        print(f"[backend] SQLiteConnector.validate_connection called")
        self.connect()
        valid = self.path.exists() or self.connected
        print(f"[backend] SQLite connection valid: {valid}")
        return valid

    def execute_query(self, query: str) -> list[dict]:
        print(f"[backend] SQLiteConnector.execute_query called with query: {query}")
        self.connect()
        result = [{"query": query, "result": "sqlite-placeholder"}]
        print(f"[backend] SQLiteConnector.execute_query result: {result}")
        return result

    def inspect_schema(self) -> dict:
        print(f"[backend] SQLiteConnector.inspect_schema called")
        self.connect()
        schema = {"dialect": "sqlite", "path": str(self.path)}
        print(f"[backend] SQLiteConnector.inspect_schema result: {schema}")
        return schema

    def list_tables(self) -> list[str]:
        print(f"[backend] SQLiteConnector.list_tables called")
        self.connect()
        tables = ["analytics_sample"]
        print(f"[backend] SQLiteConnector.list_tables result: {tables}")
        return tables

    def list_columns(self, table_name: str) -> list[str]:
        self.connect()
        return ["id", "name", "value"] if table_name else []
