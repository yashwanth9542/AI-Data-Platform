from app.providers.database.base import DatabaseConnector
from app.providers.database.mysql import MySQLConnector
from app.providers.database.postgres import PostgresConnector
from app.providers.database.sqlite import SQLiteConnector


class ConnectorFactory:
    def create(self, database_type: str) -> DatabaseConnector:
        mapping = {
            "sqlite": SQLiteConnector,
            "postgres": PostgresConnector,
            "mysql": MySQLConnector,
        }
        connector_class = mapping.get(database_type.lower())
        if connector_class is None:
            raise ValueError(f"Unsupported database type: {database_type}")
        return connector_class()

    def test_connection(self, database_type: str) -> dict[str, object]:
        connector = self.create(database_type)
        valid = connector.validate_connection()
        return {"database_type": database_type, "connected": valid}
