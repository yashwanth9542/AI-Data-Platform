from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.connection_profile import ConnectionProfile


class DatabaseConnector(ABC):
    """Common interface every SQL connector must implement.

    Extended for this refactor to accept an optional ConnectionProfile in
    the constructor, so connectors can be built from runtime connection
    parameters (host/port/credentials/ssl) supplied via the Database
    Connections view instead of only environment-derived config. This is
    additive: it doesn't change any of the abstract method contracts.
    """

    def __init__(self, profile: Optional[ConnectionProfile] = None) -> None:
        self.profile = profile
        self.connected = False

    @abstractmethod
    def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def validate_connection(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def execute_query(self, query: str) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def inspect_schema(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def list_tables(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def list_columns(self, table_name: str) -> list[str]:
        raise NotImplementedError
