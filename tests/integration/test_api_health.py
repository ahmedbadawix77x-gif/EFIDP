"""Integration tests for FastAPI health and observability endpoints."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from apps.api.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    """Create a FastAPI test client instance."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_health_checks() -> Generator[None, None, None]:
    """Mock network probes for fast, deterministic unit/integration testing."""
    with (
        patch("apps.api.routers.health.check_postgres", new_callable=AsyncMock) as m_pg,
        patch("apps.api.routers.health.check_redis", new_callable=AsyncMock) as m_redis,
        patch("apps.api.routers.health.check_minio", new_callable=AsyncMock) as m_minio,
        patch("apps.api.routers.health.check_kafka", new_callable=AsyncMock) as m_kafka,
    ):
        m_pg.return_value = {"status": "healthy", "host": "localhost", "port": 5432}
        m_redis.return_value = {"status": "healthy", "host": "localhost", "port": 6379}
        m_minio.return_value = {"status": "healthy", "endpoint": "http://localhost:9000"}
        m_kafka.return_value = {"status": "healthy", "broker": "localhost:9092"}
        yield


def test_root_health_endpoint(client: TestClient) -> None:
    """Verify that root /health endpoint responds with valid schema."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "environment" in data
    assert "services" in data
    assert data["services"]["postgres"]["status"] == "healthy"
    assert data["services"]["redis"]["status"] == "healthy"
    assert data["services"]["minio"]["status"] == "healthy"
    assert data["services"]["kafka"]["status"] == "healthy"


def test_api_v1_health_endpoint(client: TestClient) -> None:
    """Verify /api/v1/health endpoint functionality."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data


def test_metrics_endpoint(client: TestClient) -> None:
    """Verify that /metrics endpoint exposes Prometheus scrapable metrics."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert (
        "python_gc_objects_collected_total" in response.text
        or "process_virtual_memory_bytes" in response.text
    )
