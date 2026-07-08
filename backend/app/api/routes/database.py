from fastapi import APIRouter, Depends

from app.api.dependencies.container import container
from app.services.connection_service import ConnectorFactory

router = APIRouter(prefix="/database", tags=["database"])


def get_connector_factory() -> ConnectorFactory:
    return container.connector_factory


@router.get("/schema")
def schema(database_type: str = "sqlite", factory: ConnectorFactory = Depends(get_connector_factory)) -> dict:
    connector = factory.create(database_type)
    return {"database_type": database_type, "schema": connector.inspect_schema()}


@router.get("/tables")
def tables(database_type: str = "sqlite", factory: ConnectorFactory = Depends(get_connector_factory)) -> dict:
    connector = factory.create(database_type)
    return {"database_type": database_type, "tables": connector.list_tables()}


@router.get("/connect")
def connect(database_type: str = "sqlite", factory: ConnectorFactory = Depends(get_connector_factory)) -> dict:
    return factory.test_connection(database_type)


@router.post("/query")
def execute_query(database_type: str, query: str, factory: ConnectorFactory = Depends(get_connector_factory)) -> dict:
    connector = factory.create(database_type)
    return {"database_type": database_type, "rows": connector.execute_query(query)}
