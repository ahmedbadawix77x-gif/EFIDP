"""Health check router evaluating connectivity to core infrastructure services."""

import asyncio
from datetime import UTC, datetime
from typing import Any

import httpx
import redis.asyncio as aioredis
from fastapi import APIRouter

from efidp.core.config import get_settings

router = APIRouter(prefix="/api/v1", tags=["Health"])


async def check_postgres() -> dict[str, Any]:
    """Verify PostgreSQL connectivity via TCP handshake check."""
    settings = get_settings()
    host = settings.postgres.host
    port = settings.postgres.port
    try:
        # Perform asynchronous TCP connection probe
        _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=3.0)
        writer.close()
        await writer.wait_closed()
        return {"status": "healthy", "host": host, "port": port}
    except Exception as exc:
        return {"status": "unhealthy", "error": str(exc), "host": host, "port": port}


async def check_redis() -> dict[str, Any]:
    """Verify Redis availability via PING command."""
    settings = get_settings()
    host = settings.redis.host
    port = settings.redis.port
    try:
        client = aioredis.Redis(
            host=host,
            port=port,
            db=settings.redis.db,
            socket_connect_timeout=3.0,
        )
        await client.ping()
        await client.close()
        return {"status": "healthy", "host": host, "port": port}
    except Exception as exc:
        return {"status": "unhealthy", "error": str(exc), "host": host, "port": port}


async def check_minio() -> dict[str, Any]:
    """Verify MinIO object store health endpoint."""
    settings = get_settings()
    endpoint = f"{settings.minio.endpoint_url}/minio/health/live"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(endpoint)
            if resp.status_code == 200:
                return {"status": "healthy", "endpoint": settings.minio.endpoint_url}
            return {
                "status": "degraded",
                "status_code": resp.status_code,
                "endpoint": settings.minio.endpoint_url,
            }
    except Exception as exc:
        return {"status": "unhealthy", "error": str(exc), "endpoint": settings.minio.endpoint_url}


async def check_kafka() -> dict[str, Any]:
    """Verify Kafka broker reachability via TCP socket probe."""
    settings = get_settings()
    raw_addr = settings.kafka.bootstrap_servers.split(",")[0]
    if ":" in raw_addr:
        host, port_str = raw_addr.split(":")
        port = int(port_str)
    else:
        host, port = raw_addr, 9092

    try:
        _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=3.0)
        writer.close()
        await writer.wait_closed()
        return {"status": "healthy", "broker": f"{host}:{port}"}
    except Exception as exc:
        return {"status": "unhealthy", "error": str(exc), "broker": f"{host}:{port}"}


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Comprehensive infrastructure health check endpoint."""
    settings = get_settings()

    postgres_res, redis_res, minio_res, kafka_res = await asyncio.gather(
        check_postgres(),
        check_redis(),
        check_minio(),
        check_kafka(),
        return_exceptions=False,
    )

    all_healthy = all(
        svc.get("status") == "healthy" for svc in [postgres_res, redis_res, minio_res, kafka_res]
    )

    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.now(UTC).isoformat(),
        "environment": settings.environment,
        "services": {
            "postgres": postgres_res,
            "redis": redis_res,
            "minio": minio_res,
            "kafka": kafka_res,
        },
    }
