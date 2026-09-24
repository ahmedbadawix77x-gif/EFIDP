"""Data source abstractions and configuration framework for EFIDP."""

from efidp.sources.api import APIDataSource
from efidp.sources.base import BaseDataSource, ExtractionResult, SourceMetadata
from efidp.sources.config import (
    RetryPolicyConfig,
    SourceConfig,
    SourceRegistryConfig,
    get_source_config,
    load_sources_config,
)
from efidp.sources.file import FileDataSource
from efidp.sources.mock import MockDataSource

__all__ = [
    "APIDataSource",
    "BaseDataSource",
    "ExtractionResult",
    "FileDataSource",
    "MockDataSource",
    "RetryPolicyConfig",
    "SourceConfig",
    "SourceMetadata",
    "SourceRegistryConfig",
    "get_source_config",
    "load_sources_config",
]
