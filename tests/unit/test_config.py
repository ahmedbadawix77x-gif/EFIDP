"""Unit tests for efidp.core.config module."""

import os

from efidp.core.config import PlatformSettings, get_settings


def test_default_settings() -> None:
    """Verify default platform settings load with expected standard values."""
    settings = PlatformSettings()

    assert settings.environment == "development"
    assert settings.debug is True
    assert settings.log_level == "INFO"
    assert settings.log_format == "json"

    # PostgreSQL defaults
    assert settings.postgres.user == "efidp_admin"
    assert settings.postgres.port == 5432
    assert settings.postgres.database == "efidp_dw"
    assert "postgresql://" in settings.postgres.sync_dsn
    assert "postgresql+asyncpg://" in settings.postgres.async_dsn

    # MinIO defaults
    assert settings.minio.endpoint_url == "http://localhost:9000"
    assert settings.minio.bronze_bucket == "efidp-bronze"
    assert settings.minio.silver_bucket == "efidp-silver"
    assert settings.minio.gold_bucket == "efidp-gold"

    # Kafka defaults
    assert settings.kafka.bootstrap_servers == "localhost:9092"
    assert settings.kafka.topic_transactions_raw == "efidp.transactions.raw"


def test_environment_override() -> None:
    """Verify settings can be overridden via environment variables."""
    os.environ["ENVIRONMENT"] = "production"
    os.environ["DEBUG"] = "false"
    os.environ["LOG_LEVEL"] = "WARNING"
    os.environ["POSTGRES_PORT"] = "5433"
    os.environ["POSTGRES_DB"] = "efidp_dw_prod"

    settings = PlatformSettings()

    assert settings.environment == "production"
    assert settings.debug is False
    assert settings.log_level == "WARNING"
    assert settings.postgres.port == 5433
    assert settings.postgres.database == "efidp_dw_prod"
    assert ":5433/efidp_dw_prod" in settings.postgres.sync_dsn


def test_get_settings_caching() -> None:
    """Verify get_settings returns cached singleton instance."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
