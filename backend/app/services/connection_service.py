from app.providers.database.base import DatabaseConnector
from app.providers.database.mysql import MySQLConnector
from app.providers.database.postgres import PostgresConnector
from app.providers.database.sqlite import SQLiteConnector


class ConnectorFactory:
    def create(self, database_type: str) -> DatabaseConnector:
        print(f"[backend] ConnectorFactory.create called with database_type: {database_type}")
        mapping = {
            "sqlite": SQLiteConnector,
            "postgres": PostgresConnector,
            "mysql": MySQLConnector,
        }
        connector_class = mapping.get(database_type.lower())
        if connector_class is None:
            raise ValueError(f"Unsupported database type: {database_type}")
        connector = connector_class()
        print(f"[backend] Connector instance created: {connector.__class__.__name__}")
        return connector

    def test_connection(self, database_type: str) -> dict[str, object]:
        print(f"[backend] ConnectorFactory.test_connection called for: {database_type}")
        connector = self.create(database_type)
        valid = connector.validate_connection()
        print(f"[backend] Connection validation result for {database_type}: {valid}")
        return {"database_type": database_type, "connected": valid}
