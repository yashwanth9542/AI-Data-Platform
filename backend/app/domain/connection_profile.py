from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ConnectionProfile:
    """Represents a runtime, user-configured database connection.

    This replaces the previous hardcoded `database_type` string parameter
    with a full profile object so connectors can be constructed with
    host/port/credentials supplied at request time (e.g. via the
    Database Connections view, POST /api/v1/database/connect) rather than
    baked into environment variables at process start.
    """

    id: str
    database_type: str
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    ssl: bool = False
    connection_string: Optional[str] = None
    # Free-form bag for connector-specific extras (e.g. sqlite file path,
    # pool size, driver-specific flags) that don't warrant a dedicated field.
    extra: dict[str, Any] = field(default_factory=dict)

    def dsn_kwargs(self) -> dict[str, Any]:
        """Common kwargs most driver libraries (psycopg, mysqlclient, etc.) accept."""
        return {
            "host": self.host,
            "port": self.port,
            "user": self.username,
            "password": self.password,
            "dbname": self.database,
            "sslmode": "require" if self.ssl else "disable",
        }
