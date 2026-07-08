from fastapi import APIRouter

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("")
def metrics() -> dict[str, object]:
    return {
        "request_count": 0,
        "average_latency_ms": 0,
        "sql_execution_time_ms": 0,
        "llm_response_time_ms": 0,
        "error_rate": 0,
    }
