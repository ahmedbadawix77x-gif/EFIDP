"""Mock and synthetic data source connector for testing and simulation."""

import uuid
from datetime import UTC, datetime
from typing import Any

from efidp.contracts.envelope import compute_payload_hash
from efidp.sources.base import BaseDataSource, ExtractionResult
from efidp.sources.config import SourceConfig


class MockDataSource(BaseDataSource):
    """Configurable mock data source used for integration tests and synthetic simulation feeds."""

    def __init__(
        self, config: SourceConfig, mock_records: list[dict[str, Any]] | None = None
    ) -> None:
        super().__init__(config)
        self.mock_records = mock_records or []
        self.connected = True

    def validate_connection(self) -> bool:
        """Always returns True unless deliberately configured otherwise."""
        return self.connected

    def set_connection_status(self, status: bool) -> None:
        """Control connection test outcome for negative test cases."""
        self.connected = status

    def get_schema(self) -> dict[str, Any]:
        """Return the target schema definition for the mock source."""
        return {
            "source_id": self.source_id,
            "connector": "mock",
            "dataset": self.config.dataset,
            "schema_version": self.config.schema_version,
            "record_count": len(self.mock_records),
        }

    def set_mock_records(self, records: list[dict[str, Any]]) -> None:
        """Update the set of records to return on extract()."""
        self.mock_records = records

    def extract(self, **kwargs: Any) -> ExtractionResult:
        """Extract preconfigured mock records or records passed via kwargs."""
        now = datetime.now(UTC)
        records = kwargs.get("sample_records", self.mock_records)
        checksum = compute_payload_hash(records)

        return ExtractionResult(
            extraction_id=f"ext-mock-{uuid.uuid4().hex[:12]}",
            source_id=self.source_id,
            dataset_name=self.config.dataset,
            records=records,
            row_count=len(records),
            checksum_sha256=checksum,
            start_time=now,
            end_time=now,
            metadata={"mock": True, "record_count": len(records)},
        )
