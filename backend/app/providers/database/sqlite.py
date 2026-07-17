from pathlib import Path
from app.core.config import settings
from app.providers.database.base import DatabaseConnector
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Optional

class SQLiteConnector(DatabaseConnector):
    def __init__(self, path: str | None = None) -> None:
        self.path = Path(path or settings.sqlite_path)
        self.connected = False
        print(f"[backend] SQLiteConnector initialized with path: {self.path}")

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------

    def connect(self) -> None:
        print(f"[backend] SQLiteConnector.connect called")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        is_new_file = not self.path.exists()
        self.connected = True
        if is_new_file:
            # Preserve the previous placeholder behavior (an
            # `analytics_sample` table always existed) as a seeded demo
            # table, so a brand-new local sqlite file isn't just empty.
            self._seed_sample_table()

    def _get_connection(self) -> sqlite3.Connection:
        self.connect()
        conn = sqlite3.connect(str(self.path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def validate_connection(self) -> bool:
        print(f"[backend] SQLiteConnector.validate_connection called")
        try:
            with closing(self._get_connection()) as conn:
                conn.execute("SELECT 1")
            valid = True
        except sqlite3.Error as exc:
            print(f"[backend] SQLiteConnector.validate_connection failed: {exc}")
            valid = False
        print(f"[backend] SQLite connection valid: {valid}")
        return valid
    
    def execute_query(self, query: str) -> list[dict]:
        print(f"[backend] SQLiteConnector.execute_query called with query: {query}")
        # Defense in depth: SQLValidator already enforces SELECT-only
        # upstream in the graph (see SQLValidationNode), but the
        # connector shouldn't blindly trust callers either.
        if not query or query.strip().split(None, 1)[0].upper() != "SELECT":
            raise ValueError("SQLiteConnector.execute_query only allows SELECT statements")

        with closing(self._get_connection()) as conn:
            try:
                cursor = conn.execute(query)
                rows = cursor.fetchall()
            except sqlite3.Error as exc:
                print(f"[backend] SQLiteConnector.execute_query failed: {exc}")
                raise

        result = [dict(row) for row in rows]
        print(f"[backend] SQLiteConnector.execute_query returned {len(result)} row(s)")
        return result

    def inspect_schema(self) -> dict:
        print(f"[backend] SQLiteConnector.inspect_schema called")
        self.connect()
        schema = {"dialect": "sqlite", "path": str(self.path)}
        print(f"[backend] SQLiteConnector.inspect_schema result: {schema}")
        return schema

    def list_tables(self) -> list[str]:
        print(f"[backend] SQLiteConnector.list_tables called")
        with closing(self._get_connection()) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
            )
            tables = [row["name"] for row in cursor.fetchall()]
        print(f"[backend] SQLiteConnector.list_tables result: {tables}")
        return tables

    def list_columns(self, table_name: str) -> list[str]:
        print(f"[backend] SQLiteConnector.list_columns called for table: {table_name}")
        if not table_name:
            return []
        with closing(self._get_connection()) as conn:
            # PRAGMA doesn't support parameter binding; guard against
            # identifiers that aren't plain table names before interpolating.
            if not table_name.replace("_", "").isalnum():
                raise ValueError(f"Invalid table name: {table_name}")
            cursor = conn.execute(f'PRAGMA table_info("{table_name}")')
            columns = [row["name"] for row in cursor.fetchall()]
        print(f"[backend] SQLiteConnector.list_columns result: {columns}")
        return columns