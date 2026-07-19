from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.domain.connection_profile import ConnectionProfile
from app.providers.database.base import DatabaseConnector

_SEED_TABLE = "analytics_sample"


class SQLiteConnector(DatabaseConnector):
    def __init__(self, profile: Optional[ConnectionProfile] = None) -> None:
        super().__init__(profile=profile)
        path = None
        if profile is not None:
            path = profile.database or profile.extra.get("path")
        self.path = Path(path or settings.sqlite_path)
        print(f"[backend] SQLiteConnector initialized with path: {self.path}")

    def connect(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        is_new_file = not self.path.exists()
        self.connected = True
        if is_new_file:
            self._seed_sample_table()

    def _get_connection(self) -> sqlite3.Connection:
        self.connect()
        conn = sqlite3.connect(str(self.path))
        conn.row_factory = sqlite3.Row
        return conn

    def _seed_sample_table(self) -> None:
        with closing(sqlite3.connect(str(self.path))) as conn:
            conn.execute(
                f"CREATE TABLE IF NOT EXISTS {_SEED_TABLE} "
                "(id INTEGER PRIMARY KEY, name TEXT NOT NULL, value REAL NOT NULL)"
            )
            conn.execute(
                f"INSERT INTO {_SEED_TABLE} (name, value) VALUES (?, ?), (?, ?), (?, ?)",
                ("sample_a", 10.0, "sample_b", 20.5, "sample_c", 30.25),
            )
            conn.commit()

    def validate_connection(self) -> bool:
        try:
            with closing(self._get_connection()) as conn:
                conn.execute("SELECT 1")
            valid = True
        except sqlite3.Error as exc:
            print(f"[backend] SQLiteConnector.validate_connection failed: {exc}")
            valid = False
        return valid

    def execute_query(self, query: str) -> list[dict]:
        if not query or query.strip().split(None, 1)[0].upper() != "SELECT":
            raise ValueError("SQLiteConnector.execute_query only allows SELECT statements")
        with closing(self._get_connection()) as conn:
            cursor = conn.execute(query)
            rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def inspect_schema(self) -> dict:
        return {"dialect": "sqlite", "path": str(self.path)}

    def list_tables(self) -> list[str]:
        with closing(self._get_connection()) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
            )
            return [row["name"] for row in cursor.fetchall()]

    def list_columns(self, table_name: str) -> list[str]:
        if not table_name:
            return []
        with closing(self._get_connection()) as conn:
            if not table_name.replace("_", "").isalnum():
                raise ValueError(f"Invalid table name: {table_name}")
            cursor = conn.execute(f'PRAGMA table_info("{table_name}")')
            return [row["name"] for row in cursor.fetchall()]