"""FastAPI application entrypoint for EFIDP Serving Layer."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from apps.api.routers import health
from efidp.core.config import get_settings
from efidp.core.logging import configure_logging, get_logger

logger = get_logger("efidp.api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle management."""
    settings = get_settings()
    configure_logging(settings)
    logger.info("api_startup", version="0.1.0", environment=settings.environment)
    yield
    logger.info("api_shutdown")


app = FastAPI(
    title="EFIDP Serving Engine",
    description="Egypt Financial Intelligence Data Platform - Serving & Analytics API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Register health check router
app.include_router(health.router)


@app.get("/health", tags=["Health"], include_in_schema=False)
async def root_health() -> dict[str, Any]:
    """Root health check redirecting/aliasing to /api/v1/health."""
    return await health.health_check()


@app.get("/metrics", response_class=PlainTextResponse, tags=["Observability"])
def metrics() -> PlainTextResponse:
    """Expose Prometheus metrics for scraping."""
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
