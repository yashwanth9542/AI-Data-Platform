from __future__ import annotations

from app.domain.connection_profile import ConnectionProfile
from app.services.connection_service import ConnectorFactory


class SchemaService:
    """Fetches and shapes schema information for prompt construction.

    Kept separate from ConnectorFactory so caching/TTL can be added later
    (schema introspection is comparatively expensive) without touching
    graph nodes or the connector layer.
    """

    def __init__(self, connector_factory: ConnectorFactory) -> None:
        self.connector_factory = connector_factory

    def get_schema(self, profile: ConnectionProfile) -> dict:
        connector = self.connector_factory.create(profile)
        tables = connector.list_tables()
        schema = connector.inspect_schema()
        schema["tables"] = {table: connector.list_columns(table) for table in tables}
        print(f"[backend] SchemaService.get_schema resolved schema for {profile.id}: {schema}")
        return schema
