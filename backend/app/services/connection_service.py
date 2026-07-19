from __future__ import annotations

import uuid
from typing import Dict, Optional

from app.domain.connection_profile import ConnectionProfile
from app.providers.database.base import DatabaseConnector
from app.providers.database.mysql import MySQLConnector
from app.providers.database.postgres import PostgresConnector
from app.providers.database.sqlite import SQLiteConnector


class ConnectionNotFoundError(Exception):
    pass


class ConnectionProfileStore:
    """In-memory registry of connection profiles.

    v1 keeps this in memory to match the current lack of a persistence
    layer for connections (see phase1-architecture-design.md section 8,
    which only defines conversation/query history models, not connection
    profiles). Swapping this for a repository-backed store later is a
    drop-in change: callers only depend on this class's public methods.
    """

    def __init__(self) -> None:
        self._profiles: Dict[str, ConnectionProfile] = {}

    def create(self, profile: ConnectionProfile) -> ConnectionProfile:
        if not profile.id:
            profile.id = str(uuid.uuid4())
        self._profiles[profile.id] = profile
        print(f"[backend] ConnectionProfileStore.create stored profile: {profile.id} ({profile.database_type})")
        return profile

    def get(self, connection_id: str) -> ConnectionProfile:
        profile = self._profiles.get(connection_id)
        if profile is None:
            raise ConnectionNotFoundError(f"Unknown connection_id: {connection_id}")
        return profile

    def get_optional(self, connection_id: Optional[str]) -> Optional[ConnectionProfile]:
        if connection_id is None:
            return None
        return self._profiles.get(connection_id)

    def list(self) -> list[ConnectionProfile]:
        return list(self._profiles.values())

    def delete(self, connection_id: str) -> None:
        self._profiles.pop(connection_id, None)
        print(f"[backend] ConnectionProfileStore.delete removed profile: {connection_id}")

    def validate(self, connector_factory: "ConnectorFactory", connection_id: str) -> dict[str, object]:
        profile = self.get(connection_id)
        return connector_factory.test_connection(profile)


class ConnectorFactory:
    """Resolves a `ConnectionProfile` to a concrete `DatabaseConnector`.

    Previously this accepted a bare `database_type: str`, which meant a
    connector could only ever be built from process-wide environment
    configuration (e.g. settings.sqlite_path). It now accepts the full
    profile so the same process can serve multiple runtime-configured
    connections — different hosts/credentials, not just different
    database_types — from the Database Connections view.
    """

    _REGISTRY: Dict[str, type[DatabaseConnector]] = {
        "sqlite": SQLiteConnector,
        "postgres": PostgresConnector,
        "mysql": MySQLConnector,
    }

    def create(self, profile: ConnectionProfile) -> DatabaseConnector:
        print(f"[backend] ConnectorFactory.create called with profile: {profile.id} ({profile.database_type})")
        connector_class = self._REGISTRY.get(profile.database_type.lower())
        if connector_class is None:
            raise ValueError(f"Unsupported database type: {profile.database_type}")
        connector = connector_class(profile=profile)
        print(f"[backend] Connector instance created: {connector.__class__.__name__}")
        return connector

    def test_connection(self, profile: ConnectionProfile) -> dict[str, object]:
        print(f"[backend] ConnectorFactory.test_connection called for: {profile.database_type}")
        connector = self.create(profile)
        valid = connector.validate_connection()
        print(f"[backend] Connection validation result for {profile.database_type}: {valid}")
        return {"database_type": profile.database_type, "connection_id": profile.id, "connected": valid}

    @classmethod
    def register(cls, database_type: str, connector_class: type[DatabaseConnector]) -> None:
        """Extension point — see docs/provider-extension-guide.md."""
        cls._REGISTRY[database_type.lower()] = connector_class
