from fastapi import APIRouter, Depends

from app.api.dependencies.container import container
from app.services.connection_service import ConnectorFactory

router = APIRouter(prefix="/database", tags=["database"])


def get_connector_factory() -> ConnectorFactory:
    print("[backend] Injecting ConnectorFactory from container")
    return container.connector_factory


@router.get("/schema")
def schema(database_type: str = "sqlite", factory: ConnectorFactory = Depends(get_connector_factory)) -> dict:
    print(f"[backend] /database/schema called for type: {database_type}")
    connector = factory.create(database_type)
    schema = connector.inspect_schema()
    print(f"[backend] Schema inspected: {schema}")
    return {"database_type": database_type, "schema": schema}


@router.get("/tables")
def tables(database_type: str = "sqlite", factory: ConnectorFactory = Depends(get_connector_factory)) -> dict:
    print(f"[backend] /database/tables called for type: {database_type}")
    connector = factory.create(database_type)
    tables = connector.list_tables()
    print(f"[backend] Tables listed: {tables}")
    return {"database_type": database_type, "tables": tables}


@router.get("/connect")
def connect(database_type: str = "sqlite", factory: ConnectorFactory = Depends(get_connector_factory)) -> dict:
    print(f"[backend] /database/connect called for type: {database_type}")
    result = factory.test_connection(database_type)
    print(f"[backend] Connection test result: {result}")
    return result


@router.post("/query")
def execute_query(database_type: str, query: str, factory: ConnectorFactory = Depends(get_connector_factory)) -> dict:
    print(f"[backend] /database/query called for type: {database_type}, query: {query}")
    connector = factory.create(database_type)
    rows = connector.execute_query(query)
    print(f"[backend] Query execution rows count: {len(rows)}")
    return {"database_type": database_type, "rows": rows}
