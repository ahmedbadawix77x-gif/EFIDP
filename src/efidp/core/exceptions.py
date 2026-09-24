"""Centralized exception hierarchy for the EFIDP platform."""

from typing import Any


class EFIDPError(Exception):
    """Base exception class for all EFIDP platform exceptions."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ConfigurationError(EFIDPError):
    """Raised when environment variables or application configuration is invalid."""


class IngestionError(EFIDPError):
    """Raised when data ingestion from an external source or stream fails."""


class DataQualityError(EFIDPError):
    """Raised when a dataset fails a critical data quality gate check."""


class StorageError(EFIDPError):
    """Raised when object storage (MinIO/S3) or database interaction fails."""
