"""Standardized ingestion metadata envelope and generic container models."""

import hashlib
import json
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from efidp.contracts.enums import SourceClassification

T = TypeVar("T")


def compute_payload_hash(payload: Any) -> str:
    """Compute a deterministic SHA-256 hash of any JSON-serializable payload."""
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class IngestionMetadata(BaseModel):
    """Standardized metadata envelope accompanying every raw ingestion batch."""

    ingestion_id: str = Field(
        ...,
        min_length=8,
        description="Unique identifier for the specific ingestion execution instance",
        examples=["ingest-cbe-20240310-090000"],
    )
    source_id: str = Field(
        ...,
        min_length=2,
        max_length=64,
        description="Registered identifier of the originating data source",
        examples=["cbe_open_statistics"],
    )
    source_type: SourceClassification = Field(
        ...,
        description="Origin classification of the data (real_public, synthetic, derived)",
    )
    dataset_name: str = Field(
        ...,
        min_length=2,
        max_length=64,
        description="Canonical target dataset name",
        examples=["economic_indicators"],
    )
    extracted_at: datetime = Field(
        ...,
        description="UTC timestamp when extraction completed and envelope was sealed",
    )
    schema_version: str = Field(
        ...,
        min_length=3,
        max_length=16,
        description="Semantic version of the target schema contract (e.g., 1.0.0)",
        examples=["1.0.0"],
    )
    payload_hash: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="SHA-256 cryptographic checksum of the raw extracted payload",
        examples=["e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"],
    )
    row_count: int = Field(
        ...,
        ge=0,
        description="Number of records contained within the extraction batch",
        examples=[100],
    )
    extraction_start_time: datetime = Field(
        ...,
        description="UTC timestamp marking the start of the data extraction phase",
    )
    extraction_end_time: datetime = Field(
        ...,
        description="UTC timestamp marking the completion of the data extraction phase",
    )

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    @field_validator("payload_hash")
    @classmethod
    def validate_hash_format(cls, v: str) -> str:
        """Verify that payload_hash is a valid 64-character lowercase hexadecimal string."""
        if len(v) != 64 or not all(c in "0123456789abcdefABCDEF" for c in v):
            raise ValueError("payload_hash must be a 64-character hexadecimal SHA-256 string")
        return v.lower()

    @model_validator(mode="after")
    def validate_time_window(self) -> "IngestionMetadata":
        """Verify that extraction end time is chronologically greater than or equal to start time."""
        if self.extraction_end_time < self.extraction_start_time:
            raise ValueError(
                f"extraction_end_time ({self.extraction_end_time.isoformat()}) cannot precede "
                f"extraction_start_time ({self.extraction_start_time.isoformat()})"
            )
        return self


class IngestionEnvelope(BaseModel, Generic[T]):
    """Generic container wrapping batch payloads with standardized ingestion metadata."""

    metadata: IngestionMetadata
    payload: T

    model_config = ConfigDict(extra="forbid")
