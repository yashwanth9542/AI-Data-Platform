from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.chat import router as chat_router
from app.api.routes.database import router as database_router
from app.api.routes.health import router as health_router
from app.api.routes.history import router as history_router
from app.api.routes.metrics import router as metrics_router
from app.core.exceptions import AIPlatformError
from app.core.logging import logger

print("[backend] Initializing FastAPI application")
app = FastAPI(title="AI Data Platform", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("[backend] FastAPI startup event triggered")

@app.exception_handler(AIPlatformError)
async def ai_platform_error_handler(_: Request, exc: AIPlatformError) -> JSONResponse:
    print(f"[backend] AIPlatformError caught: {exc}")
    logger.warning("platform_error", extra={"error": str(exc)})
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    print(f"[backend] Request validation error: {exc.errors()}")
    logger.warning("validation_error", extra={"error": exc.errors()})
    return JSONResponse(status_code=422, content={"detail": "Invalid request payload"})

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"[backend] HTTP request received: {request.method} {request.url.path}")
    logger.info("request_started", extra={"path": request.url.path, "method": request.method})
    response = await call_next(request)
    print(f"[backend] HTTP request completed: {request.method} {request.url.path} -> {response.status_code}")
    logger.info("request_completed", extra={"path": request.url.path, "status_code": response.status_code})
    return response

app.include_router(health_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(history_router, prefix="/api/v1")
app.include_router(database_router, prefix="/api/v1")
app.include_router(metrics_router, prefix="/api/v1")
