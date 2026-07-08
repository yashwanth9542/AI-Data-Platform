from app.providers.database.base import DatabaseConnector


class SQLiteConnector(DatabaseConnector):
    def connect(self) -> None:
        return None

    def validate_connection(self) -> bool:
        return True

    def execute_query(self, query: str) -> list[dict]:
        return [{"query": query, "result": "placeholder"}]

    def inspect_schema(self) -> dict:
        return {"dialect": "sqlite"}

    def list_tables(self) -> list[str]:
        return ["analytics_sample"]

    def list_columns(self, table_name: str) -> list[str]:
        return ["id", "name", "value"]
