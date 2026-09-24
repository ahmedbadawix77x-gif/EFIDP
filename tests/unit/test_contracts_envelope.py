"""Unit tests for IngestionMetadata and IngestionEnvelope."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from efidp.contracts.enums import SourceClassification
from efidp.contracts.envelope import (
    IngestionEnvelope,
    IngestionMetadata,
    compute_payload_hash,
)


def test_valid_ingestion_metadata() -> None:
    now = datetime.now(UTC)
    meta = IngestionMetadata(
        ingestion_id="ingest-cbe-20240310-090000",
        source_id="cbe_open_statistics",
        source_type=SourceClassification.REAL_PUBLIC,
        dataset_name="economic_indicators",
        extracted_at=now,
        schema_version="1.0.0",
        payload_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        row_count=100,
        extraction_start_time=now - timedelta(seconds=10),
        extraction_end_time=now,
    )

    assert meta.ingestion_id == "ingest-cbe-20240310-090000"
    assert meta.row_count == 100
    assert meta.payload_hash == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_invalid_payload_hash() -> None:
    now = datetime.now(UTC)
    # Short length
    with pytest.raises(ValidationError):
        IngestionMetadata(
            ingestion_id="ingest-bad-hash",
            source_id="cbe",
            source_type=SourceClassification.REAL_PUBLIC,
            dataset_name="economic_indicators",
            extracted_at=now,
            schema_version="1.0.0",
            payload_hash="too_short",
            row_count=1,
            extraction_start_time=now,
            extraction_end_time=now,
        )

    # 64 chars but non-hex
    with pytest.raises(ValidationError) as exc:
        IngestionMetadata(
            ingestion_id="ingest-bad-hash",
            source_id="cbe",
            source_type=SourceClassification.REAL_PUBLIC,
            dataset_name="economic_indicators",
            extracted_at=now,
            schema_version="1.0.0",
            payload_hash="z" * 64,
            row_count=1,
            extraction_start_time=now,
            extraction_end_time=now,
        )
    assert "payload_hash must be a 64-character hexadecimal" in str(exc.value)


def test_extraction_end_before_start() -> None:
    now = datetime.now(UTC)
    with pytest.raises(ValidationError) as exc:
        IngestionMetadata(
            ingestion_id="ingest-bad-time",
            source_id="cbe",
            source_type=SourceClassification.REAL_PUBLIC,
            dataset_name="economic_indicators",
            extracted_at=now,
            schema_version="1.0.0",
            payload_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            row_count=1,
            extraction_start_time=now,
            extraction_end_time=now - timedelta(seconds=5),
        )
    assert "extraction_end_time" in str(exc.value)
    assert "cannot precede extraction_start_time" in str(exc.value)


def test_compute_payload_hash_deterministic() -> None:
    data1 = {"a": 1, "b": [2, 3]}
    data2 = {"b": [2, 3], "a": 1}
    assert compute_payload_hash(data1) == compute_payload_hash(data2)
    assert len(compute_payload_hash(data1)) == 64


def test_ingestion_envelope_generic() -> None:
    now = datetime.now(UTC)
    meta = IngestionMetadata(
        ingestion_id="ingest-tx-test-01",
        source_id="mock_source",
        source_type=SourceClassification.SYNTHETIC,
        dataset_name="financial_transactions",
        extracted_at=now,
        schema_version="1.0.0",
        payload_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        row_count=1,
        extraction_start_time=now - timedelta(seconds=1),
        extraction_end_time=now,
    )
    envelope = IngestionEnvelope[list[dict[str, str]]](
        metadata=meta,
        payload=[{"sample_key": "sample_val"}],
    )
    assert envelope.payload[0]["sample_key"] == "sample_val"
    assert envelope.metadata.dataset_name == "financial_transactions"
