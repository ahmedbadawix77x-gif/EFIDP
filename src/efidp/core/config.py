"""Platform configuration module using Pydantic Settings.

Reads typed configuration from environment variables and optional .env files.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    """PostgreSQL analytical warehouse and metastore connection settings."""

    user: str = Field(default="efidp_admin", validation_alias="POSTGRES_USER")
    password: str = Field(
        default="efidp_dev_secret_change_in_prod",
        validation_alias="POSTGRES_PASSWORD",
    )
    host: str = Field(default="localhost", validation_alias="POSTGRES_HOST")
    port: int = Field(default=5432, validation_alias="POSTGRES_PORT")
    database: str = Field(default="efidp_dw", validation_alias="POSTGRES_DB")

    @property
    def sync_dsn(self) -> str:
        """Construct synchronous PostgreSQL DSN string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def async_dsn(self) -> str:
        """Construct asynchronous PostgreSQL DSN string for asyncpg."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class MinioSettings(BaseSettings):
    """MinIO S3-compatible Lakehouse object storage settings."""

    endpoint_url: str = Field(
        default="http://localhost:9000", validation_alias="MINIO_ENDPOINT_URL"
    )
    access_key: str = Field(default="minioadmin", validation_alias="MINIO_ACCESS_KEY")
    secret_key: str = Field(default="minioadmin_secret_dev", validation_alias="MINIO_SECRET_KEY")
    bronze_bucket: str = Field(default="efidp-bronze", validation_alias="MINIO_BRONZE_BUCKET")
    silver_bucket: str = Field(default="efidp-silver", validation_alias="MINIO_SILVER_BUCKET")
    gold_bucket: str = Field(default="efidp-gold", validation_alias="MINIO_GOLD_BUCKET")
    secure: bool = Field(default=False, validation_alias="MINIO_SECURE")


class KafkaSettings(BaseSettings):
    """Apache Kafka event broker settings."""

    bootstrap_servers: str = Field(
        default="localhost:9092", validation_alias="KAFKA_BOOTSTRAP_SERVERS"
    )
    topic_transactions_raw: str = Field(
        default="efidp.transactions.raw",
        validation_alias="KAFKA_TOPIC_TRANSACTIONS_RAW",
    )
    topic_deadletter: str = Field(
        default="efidp.transactions.deadletter",
        validation_alias="KAFKA_TOPIC_DEADLETTER",
    )
    consumer_group: str = Field(
        default="efidp-stream-workers", validation_alias="KAFKA_CONSUMER_GROUP"
    )


class RedisSettings(BaseSettings):
    """Redis cache and in-memory store settings."""

    host: str = Field(default="localhost", validation_alias="REDIS_HOST")
    port: int = Field(default=6379, validation_alias="REDIS_PORT")
    db: int = Field(default=0, validation_alias="REDIS_DB")


class PlatformSettings(BaseSettings):
    """Unified application settings containing all platform subsystems."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["development", "staging", "production", "testing"] = Field(
        default="development", validation_alias="ENVIRONMENT"
    )
    debug: bool = Field(default=True, validation_alias="DEBUG")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", validation_alias="LOG_LEVEL"
    )
    log_format: Literal["json", "console"] = Field(default="json", validation_alias="LOG_FORMAT")

    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
    minio: MinioSettings = Field(default_factory=MinioSettings)
    kafka: KafkaSettings = Field(default_factory=KafkaSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)


@lru_cache(maxsize=1)
def get_settings() -> PlatformSettings:
    """Return cached platform settings singleton instance."""
    return PlatformSettings()
