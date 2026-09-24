"""Pydantic configuration models and YAML loaders for data source registries."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

from efidp.contracts.enums import ConnectorType, SourceClassification
from efidp.core.exceptions import SourceConfigurationError


class RetryPolicyConfig(BaseModel):
    """Network request retry and backoff parameters."""

    max_retries: int = Field(
        default=3, ge=0, le=10, description="Maximum retry attempts on failure"
    )
    backoff_factor: float = Field(
        default=2.0, ge=1.0, le=10.0, description="Multiplier for exponential backoff delay"
    )
    timeout_seconds: float = Field(
        default=30.0, gt=0.0, le=300.0, description="Socket and read timeout in seconds"
    )

    model_config = ConfigDict(extra="forbid")


class SourceConfig(BaseModel):
    """Specification describing a single data source integration."""

    source_id: str = Field(
        ..., min_length=2, max_length=64, description="Unique identifier for the source"
    )
    source_name: str = Field(
        ..., min_length=2, max_length=128, description="Descriptive display name"
    )
    source_type: SourceClassification = Field(
        ..., description="Data origin classification (real_public, synthetic, derived)"
    )
    dataset: str = Field(..., min_length=2, max_length=64, description="Target dataset name")
    schema_version: str = Field(default="1.0.0", description="Contract schema version")
    connector_type: ConnectorType = Field(
        ..., description="Underlying connector protocol (api, file, streaming, mock)"
    )
    endpoint: str | None = Field(default=None, description="HTTP endpoint URL if connector is API")
    path: str | None = Field(
        default=None, description="Local or object storage path if connector is File"
    )
    enabled: bool = Field(default=True, description="Whether this source is active for ingestion")
    retry_policy: RetryPolicyConfig = Field(default_factory=RetryPolicyConfig)
    schedule_cron: str | None = Field(
        default=None, description="Standard cron expression for ingestion cadence"
    )
    extra_params: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary adapter-specific parameters"
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("endpoint")
    @classmethod
    def validate_endpoint_for_api(cls, v: str | None, info: Any) -> str | None:
        """Verify endpoint exists if connector is API."""
        connector = info.data.get("connector_type")
        if connector == ConnectorType.API and not v:
            raise ValueError("endpoint is required when connector_type is 'api'")
        return v


class SourceRegistryConfig(BaseModel):
    """Top-level configuration container for sources.yaml."""

    version: str = Field(default="1.0", description="Configuration format version")
    sources: list[SourceConfig] = Field(
        ..., min_length=1, description="List of configured data sources"
    )

    model_config = ConfigDict(extra="forbid")


def load_sources_config(file_path: Path | str | None = None) -> SourceRegistryConfig:
    """Load, parse, and validate the sources registry from a YAML file.

    If file_path is None, defaults to config/sources.yaml in the project root.
    """
    if file_path is None:
        path = Path(__file__).resolve().parents[3] / "config" / "sources.yaml"
    else:
        path = Path(file_path)

    if not path.is_file():
        raise SourceConfigurationError(f"Sources configuration file not found at: {path}")

    try:
        with open(path, encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)
    except Exception as e:
        raise SourceConfigurationError(f"Failed to read sources YAML file: {e}") from e

    if not isinstance(raw_data, dict):
        raise SourceConfigurationError(
            f"Sources YAML root must be a mapping, got {type(raw_data).__name__}"
        )

    try:
        return SourceRegistryConfig.model_validate(raw_data)
    except Exception as e:
        raise SourceConfigurationError(
            f"Sources configuration schema validation failed: {e}"
        ) from e


def get_source_config(source_id: str, file_path: Path | str | None = None) -> SourceConfig:
    """Retrieve a single source configuration by its source_id."""
    registry = load_sources_config(file_path)
    for src in registry.sources:
        if src.source_id == source_id:
            return src
    raise SourceConfigurationError(f"Data source with id '{source_id}' not found in registry")
