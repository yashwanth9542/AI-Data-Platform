from app.core.config import settings
from app.core.exceptions import DatabaseConnectionError
from app.providers.database.base import DatabaseConnector


class PostgresConnector(DatabaseConnector):
    def __init__(self, dsn: str | None = None) -> None:
        self.dsn = dsn or settings.postgres_dsn
        self.connected = False

    def connect(self) -> None:
        if not self.dsn:
            raise DatabaseConnectionError("POSTGRES_DSN is not configured")
        self.connected = True

    def validate_connection(self) -> bool:
        self.connect()
        return self.connected

    def execute_query(self, query: str) -> list[dict]:
        self.connect()
        return [{"query": query, "result": "postgres-placeholder"}]

    def inspect_schema(self) -> dict:
        self.connect()
        return {"dialect": "postgres", "dsn": self.dsn}

    def list_tables(self) -> list[str]:
        self.connect()
        return ["analytics_sample"]

    def list_columns(self, table_name: str) -> list[str]:
        self.connect()
        return ["id", "name", "value"] if table_name else []
