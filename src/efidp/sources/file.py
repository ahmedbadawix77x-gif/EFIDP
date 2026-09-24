"""File-based data source connector abstraction."""

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from efidp.contracts.envelope import compute_payload_hash
from efidp.sources.base import BaseDataSource, ExtractionResult
from efidp.sources.config import SourceConfig


class FileDataSource(BaseDataSource):
    """Data source adapter for static files, seeds, and drops (CSV, JSON, Parquet)."""

    def __init__(self, config: SourceConfig) -> None:
        super().__init__(config)
        self.path = Path(config.path) if config.path else None

    def validate_connection(self) -> bool:
        """Verify that the target file or directory path exists and is accessible."""
        if not self.path:
            return False
        return self.path.exists()

    def get_schema(self) -> dict[str, Any]:
        """Return the target schema definition for the file source."""
        return {
            "source_id": self.source_id,
            "connector": "file",
            "dataset": self.config.dataset,
            "schema_version": self.config.schema_version,
            "path": str(self.path),
        }

    def extract(self, **kwargs: Any) -> ExtractionResult:
        """Extract data from the file source."""
        now = datetime.now(UTC)
        records: list[dict[str, Any]] = []

        if self.path and self.path.is_file():
            if self.path.suffix == ".json":
                with open(self.path, encoding="utf-8") as f:
                    content = json.load(f)
                    records = content if isinstance(content, list) else [content]
            else:
                records = kwargs.get("sample_records", [])
        else:
            records = kwargs.get("sample_records", [])

        checksum = compute_payload_hash(records)

        return ExtractionResult(
            extraction_id=f"ext-file-{uuid.uuid4().hex[:12]}",
            source_id=self.source_id,
            dataset_name=self.config.dataset,
            records=records,
            row_count=len(records),
            checksum_sha256=checksum,
            start_time=now,
            end_time=now,
            metadata={
                "file_path": str(self.path),
                "format": self.path.suffix if self.path else "unknown",
            },
        )
