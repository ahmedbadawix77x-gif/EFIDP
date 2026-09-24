"""REST API data source connector abstraction."""

import uuid
from datetime import UTC, datetime
from typing import Any

from efidp.contracts.envelope import compute_payload_hash
from efidp.sources.base import BaseDataSource, ExtractionResult
from efidp.sources.config import SourceConfig


class APIDataSource(BaseDataSource):
    """Data source adapter for remote RESTful APIs (e.g. World Bank, CBE Open Data)."""

    def __init__(self, config: SourceConfig) -> None:
        super().__init__(config)
        self.endpoint = config.endpoint

    def validate_connection(self) -> bool:
        """Validate connection readiness to API endpoint."""
        # Verifies that endpoint configuration is a valid URI scheme
        if not self.endpoint:
            return False
        return self.endpoint.startswith("http://") or self.endpoint.startswith("https://")

    def get_schema(self) -> dict[str, Any]:
        """Return the target schema definition for the API source."""
        return {
            "source_id": self.source_id,
            "connector": "api",
            "dataset": self.config.dataset,
            "schema_version": self.config.schema_version,
            "endpoint": self.endpoint,
        }

    def extract(self, **kwargs: Any) -> ExtractionResult:
        """Execute extraction call against API endpoint.

        NOTE: Full HTTP client session with retry/backoff is implemented in Phase 4.
        """
        now = datetime.now(UTC)
        records: list[dict[str, Any]] = kwargs.get("sample_records", [])
        checksum = compute_payload_hash(records)

        return ExtractionResult(
            extraction_id=f"ext-api-{uuid.uuid4().hex[:12]}",
            source_id=self.source_id,
            dataset_name=self.config.dataset,
            records=records,
            row_count=len(records),
            checksum_sha256=checksum,
            start_time=now,
            end_time=now,
            metadata={"endpoint": self.endpoint, "status": "simulated_extract"},
        )
