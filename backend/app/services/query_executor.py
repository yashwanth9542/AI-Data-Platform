from __future__ import annotations

import time

from app.domain.connection_profile import ConnectionProfile
from app.services.connection_service import ConnectorFactory


class QueryExecutor:
    """Executes validated SQL against the active connection and captures
    basic timing metrics (see phase1-architecture-design.md section 11.2,
    "SQL execution time").
    """

    def __init__(self, connector_factory: ConnectorFactory) -> None:
        self.connector_factory = connector_factory

    def execute(self, profile: ConnectionProfile, sql: str) -> tuple[list[dict], float]:
        connector = self.connector_factory.create(profile)
        start = time.perf_counter()
        results = connector.execute_query(sql)
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"[backend] QueryExecutor.execute finished in {elapsed_ms:.2f}ms, rows={len(results)}")
        return results, elapsed_ms
