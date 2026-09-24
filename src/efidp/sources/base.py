"""Base abstract class and result interfaces for EFIDP data sources."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from efidp.contracts.enums import ConnectorType, SourceClassification
from efidp.sources.config import SourceConfig


class SourceMetadata(BaseModel):
    """Runtime metadata describing an initialized data source."""

    source_id: str
    source_name: str
    source_type: SourceClassification
    connector_type: ConnectorType
    dataset: str
    schema_version: str
    enabled: bool

    model_config = ConfigDict(frozen=True)


class ExtractionResult(BaseModel):
    """Standardized result returned by all EFIDP data source extractors."""

    extraction_id: str = Field(..., description="Unique extraction run execution identifier")
    source_id: str = Field(..., description="ID of the data source that performed the extraction")
    dataset_name: str = Field(..., description="Canonical dataset name")
    records: list[dict[str, Any]] = Field(..., description="Raw records extracted from the source")
    row_count: int = Field(..., ge=0, description="Total count of records extracted")
    checksum_sha256: str = Field(..., description="SHA-256 hash of extracted records payload")
    start_time: datetime = Field(..., description="Extraction starting UTC timestamp")
    end_time: datetime = Field(..., description="Extraction completion UTC timestamp")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Source-specific extraction diagnostics"
    )

    model_config = ConfigDict(extra="forbid")


class BaseDataSource(ABC):
    """Abstract base class defining the standard lifecycle for data source connectors.

    Phase 4 ingestion workers interact solely through this abstraction layer.
    """

    def __init__(self, config: SourceConfig) -> None:
        """Initialize data source with validated configuration."""
        self.config = config

    @property
    def source_id(self) -> str:
        """Return the unique source identifier."""
        return self.config.source_id

    @property
    def source_type(self) -> SourceClassification:
        """Return the source origin classification."""
        return self.config.source_type

    def get_metadata(self) -> SourceMetadata:
        """Return runtime metadata for the source."""
        return SourceMetadata(
            source_id=self.config.source_id,
            source_name=self.config.source_name,
            source_type=self.config.source_type,
            connector_type=self.config.connector_type,
            dataset=self.config.dataset,
            schema_version=self.config.schema_version,
            enabled=self.config.enabled,
        )

    @abstractmethod
    def validate_connection(self) -> bool:
        """Test and verify connectivity to the underlying source."""
        raise NotImplementedError

    @abstractmethod
    def get_schema(self) -> dict[str, Any]:
        """Retrieve the formal schema definition expected from this source."""
        raise NotImplementedError

    @abstractmethod
    def extract(self, **kwargs: Any) -> ExtractionResult:
        """Extract a batch of records from the data source."""
        raise NotImplementedError
