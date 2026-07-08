from abc import ABC, abstractmethod


class DatabaseConnector(ABC):
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
