"""Unit tests for ContractValidator service."""

import json
from pathlib import Path

import pytest

from efidp.contracts.indicator import EconomicIndicatorRecord
from efidp.contracts.market import MarketObservationRecord
from efidp.contracts.transaction import FinancialTransactionEvent
from efidp.contracts.validator import ContractValidator


def test_validator_single_valid_transaction() -> None:
    sample_path = Path(__file__).resolve().parents[2] / "data" / "sample" / "valid_transaction.json"
    with open(sample_path, encoding="utf-8") as f:
        data = json.load(f)
    data.pop("_disclaimer", None)

    res = ContractValidator.validate_record(FinancialTransactionEvent, data)
    assert res.is_valid is True
    assert res.dataset_name == "financial_transactions"
    assert res.schema_version == "1.0.0"
    assert len(res.errors) == 0
    assert res.record_id == "tx-cai-20240315-091428-a89f"
    assert res.validated_data is not None


def test_validator_single_invalid_transaction() -> None:
    sample_path = (
        Path(__file__).resolve().parents[2] / "data" / "sample" / "invalid_transaction.json"
    )
    with open(sample_path, encoding="utf-8") as f:
        data = json.load(f)
    data.pop("_disclaimer", None)

    res = ContractValidator.validate_record(FinancialTransactionEvent, data)
    assert res.is_valid is False
    assert len(res.errors) > 0
    # Check that error fields include governorate, channel, amount_egp, status, risk_score
    error_fields = [e.field for e in res.errors]
    assert any("amount_egp" in f for f in error_fields)
    assert any("channel" in f for f in error_fields)
    assert any("governorate" in f for f in error_fields)


def test_validator_batch_processing() -> None:
    sample_path = Path(__file__).resolve().parents[2] / "data" / "sample" / "valid_transaction.json"
    with open(sample_path, encoding="utf-8") as f:
        valid_data = json.load(f)
    valid_data.pop("_disclaimer", None)

    invalid_data = valid_data.copy()
    invalid_data["transaction_id"] = "tx-cai-invalid"
    invalid_data["amount_egp"] = -10.0

    batch = [valid_data, invalid_data]
    batch_res = ContractValidator.validate_batch(FinancialTransactionEvent, batch)

    assert batch_res.total_records == 2
    assert batch_res.valid_records == 1
    assert batch_res.invalid_records == 1
    assert batch_res.pass_rate == 0.5
    assert batch_res.is_valid is False
    assert len(batch_res.errors_summary) > 0


def test_validator_batch_empty() -> None:
    batch_res = ContractValidator.validate_batch(FinancialTransactionEvent, [])
    assert batch_res.total_records == 0
    assert batch_res.is_valid is True
    assert batch_res.pass_rate == 1.0


def test_validator_economic_indicator() -> None:
    valid_path = (
        Path(__file__).resolve().parents[2] / "data" / "sample" / "valid_economic_indicator.json"
    )
    with open(valid_path, encoding="utf-8") as f:
        valid_ind = json.load(f)

    res_valid = ContractValidator.validate_record(EconomicIndicatorRecord, valid_ind)
    assert res_valid.is_valid is True
    assert res_valid.record_id == "CBE_CORRIDOR_LENDING"

    invalid_path = (
        Path(__file__).resolve().parents[2] / "data" / "sample" / "invalid_economic_indicator.json"
    )
    with open(invalid_path, encoding="utf-8") as f:
        invalid_ind = json.load(f)

    res_invalid = ContractValidator.validate_record(EconomicIndicatorRecord, invalid_ind)
    assert res_invalid.is_valid is False
    assert len(res_invalid.errors) > 0


def test_validator_market_record() -> None:
    valid_path = (
        Path(__file__).resolve().parents[2] / "data" / "sample" / "valid_market_record.json"
    )
    with open(valid_path, encoding="utf-8") as f:
        valid_mkt = json.load(f)

    res_valid = ContractValidator.validate_record(MarketObservationRecord, valid_mkt)
    assert res_valid.is_valid is True
    assert res_valid.record_id == "EGX30"

    invalid_path = (
        Path(__file__).resolve().parents[2] / "data" / "sample" / "invalid_market_record.json"
    )
    with open(invalid_path, encoding="utf-8") as f:
        invalid_mkt = json.load(f)

    res_invalid = ContractValidator.validate_record(MarketObservationRecord, invalid_mkt)
    assert res_invalid.is_valid is False


def test_validator_envelope_validation() -> None:
    envelope_path = Path(__file__).resolve().parents[2] / "data" / "sample" / "valid_envelope.json"
    with open(envelope_path, encoding="utf-8") as f:
        envelope_data = json.load(f)

    # Valid with nested batch payload validation
    res = ContractValidator.validate_envelope(
        envelope_data, payload_contract_cls=FinancialTransactionEvent
    )
    assert res.is_valid is True
    assert res.record_id == "ingest-synthetic-tx-20240315-001"

    # Invalid metadata
    bad_meta_envelope = {
        "metadata": {
            "ingestion_id": "short",
            "source_id": "cbe",
            "source_type": "invalid_origin",
        },
        "payload": [],
    }
    res_bad_meta = ContractValidator.validate_envelope(bad_meta_envelope)
    assert res_bad_meta.is_valid is False

    # Valid metadata but invalid payload list
    bad_payload_envelope = dict(envelope_data)
    bad_payload_envelope["payload"] = [{"invalid_key": 123}]
    res_bad_payload = ContractValidator.validate_envelope(
        bad_payload_envelope, payload_contract_cls=FinancialTransactionEvent
    )
    assert res_bad_payload.is_valid is False

    # Valid metadata with single dict payload
    single_envelope = {
        "metadata": envelope_data["metadata"],
        "payload": envelope_data["payload"][0],
    }
    res_single = ContractValidator.validate_envelope(
        single_envelope, payload_contract_cls=FinancialTransactionEvent
    )
    assert res_single.is_valid is True

    # Valid metadata with single dict payload that is invalid
    single_envelope_bad = {
        "metadata": envelope_data["metadata"],
        "payload": {"invalid_data": True},
    }
    res_single_bad = ContractValidator.validate_envelope(
        single_envelope_bad, payload_contract_cls=FinancialTransactionEvent
    )
    assert res_single_bad.is_valid is False

    # Valid metadata with scalar payload that is neither list nor dict
    scalar_envelope = {
        "metadata": envelope_data["metadata"],
        "payload": 12345,
    }
    res_scalar = ContractValidator.validate_envelope(
        scalar_envelope, payload_contract_cls=FinancialTransactionEvent
    )
    assert res_scalar.is_valid is False
    assert any("Payload must be a list or dict" in err.message for err in res_scalar.errors)

    # Valid metadata with envelope and no payload contract specified
    res_no_payload_contract = ContractValidator.validate_envelope(
        envelope_data, payload_contract_cls=None
    )
    assert res_no_payload_contract.is_valid is True


def test_validator_custom_record_id_field() -> None:
    sample_path = Path(__file__).resolve().parents[2] / "data" / "sample" / "valid_transaction.json"
    with open(sample_path, encoding="utf-8") as f:
        data = json.load(f)
    data.pop("_disclaimer", None)
    data["custom_ref_id"] = "custom-ref-999"

    res = ContractValidator.validate_record(
        FinancialTransactionEvent, data, record_id_field="custom_ref_id"
    )
    assert res.record_id == "custom-ref-999"


def test_base_contract_not_implemented() -> None:
    from efidp.contracts.base import BaseDataContract

    with pytest.raises(NotImplementedError):
        BaseDataContract.get_contract_metadata()
