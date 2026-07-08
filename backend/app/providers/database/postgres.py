from app.core.config import settings
from app.core.exceptions import DatabaseConnectionError
from app.providers.database.base import DatabaseConnector


class PostgresConnector(DatabaseConnector):
    def __init__(self, dsn: str | None = None) -> None:
        self.dsn = dsn or settings.postgres_dsn
        self.connected = False
        print(f"[backend] PostgresConnector initialized with DSN: {self.dsn}")

    def connect(self) -> None:
        print("[backend] PostgresConnector.connect called")
        if not self.dsn:
            raise DatabaseConnectionError("POSTGRES_DSN is not configured")
        self.connected = True
        print("[backend] PostgresConnector connected")

    def validate_connection(self) -> bool:
        print("[backend] PostgresConnector.validate_connection called")
        self.connect()
        print(f"[backend] PostgresConnector connected: {self.connected}")
        return self.connected

    def execute_query(self, query: str) -> list[dict]:
        print(f"[backend] PostgresConnector.execute_query called with query: {query}")
        self.connect()
        result = [{"query": query, "result": "postgres-placeholder"}]
        print(f"[backend] PostgresConnector.execute_query result: {result}")
        return result

    def inspect_schema(self) -> dict:
        print("[backend] PostgresConnector.inspect_schema called")
        self.connect()
        schema = {"dialect": "postgres", "dsn": self.dsn}
        print(f"[backend] PostgresConnector.inspect_schema result: {schema}")
        return schema

    def list_tables(self) -> list[str]:
        print("[backend] PostgresConnector.list_tables called")
        self.connect()
        tables = ["analytics_sample"]
        print(f"[backend] PostgresConnector.list_tables result: {tables}")
        return tables

    def list_columns(self, table_name: str) -> list[str]:
        self.connect()
        return ["id", "name", "value"] if table_name else []
