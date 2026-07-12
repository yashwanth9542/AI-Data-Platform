import importlib
from typing import Any

from app.core.config import settings
from app.core.exceptions import DatabaseConnectionError
from app.providers.database.base import DatabaseConnector


class MySQLConnector(DatabaseConnector):
    def __init__(self, dsn: str | None = None) -> None:
        self.dsn = dsn or settings.mysql_dsn
        self.connected = False
        self._connection = None
        print(f"[backend] MySQLConnector initialized with DSN: {self.dsn}")

    def connect(self) -> None:
        print("[backend] MySQLConnector.connect called")
        if not self.dsn:
            raise DatabaseConnectionError("MYSQL_DSN is not configured")

        try:
            connector_module = importlib.import_module("mysql.connector")
        except ImportError as exc:
            print("[backend] MySQLConnector failed to import mysql.connector")
            raise DatabaseConnectionError("mysql-connector-python is not installed") from exc

        self._connection = connector_module.connect(dsn=self.dsn)
        self.connected = True
        print("[backend] MySQLConnector connected")

    def validate_connection(self) -> bool:
        print("[backend] MySQLConnector.validate_connection called")
        try:
            self.connect()
            if self._connection is not None:
                self._connection.close()
                self._connection = None
            self.connected = False
            print("[backend] MySQLConnector connection validated")
            return True
        except DatabaseConnectionError:
            print("[backend] MySQLConnector validation failed")
            return False

    def execute_query(self, query: str) -> list[dict[str, Any]]:
        print(f"[backend] MySQLConnector.execute_query called with query: {query}")
        self.connect()
        try:
            cursor = self._connection.cursor(dictionary=True)
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            self._connection.close()
            self._connection = None
            self.connected = False
            print(f"[backend] MySQLConnector.execute_query returned {len(rows)} rows")
            return rows
        except Exception as exc:
            if self._connection is not None:
                self._connection.close()
                self._connection = None
            self.connected = False
            print(f"[backend] MySQLConnector.execute_query failed: {exc}")
            raise DatabaseConnectionError(f"MySQL query execution failed: {exc}") from exc

    def inspect_schema(self) -> dict[str, Any]:
        self.connect()
        return {"dialect": "mysql", "dsn": self.dsn}

    def list_tables(self) -> list[str]:
        self.connect()
        cursor = self._connection.cursor()
        cursor.execute("SHOW TABLES")
        rows = cursor.fetchall()
        cursor.close()
        self._connection.close()
        self._connection = None
        self.connected = False
        return [row[0] for row in rows]

    def list_columns(self, table_name: str) -> list[str]:
        self.connect()
        cursor = self._connection.cursor()
        cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
        rows = cursor.fetchall()
        cursor.close()
        self._connection.close()
        self._connection = None
        self.connected = False
        return [row[0] for row in rows]
