"""Unit tests for FinancialTransactionEvent contract."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from efidp.contracts.enums import (
    ChannelType,
    Governorate,
    SourceClassification,
    TransactionCategory,
    TransactionStatus,
)
from efidp.contracts.transaction import SCHEMA_VERSION, FinancialTransactionEvent


def test_valid_transaction_creation() -> None:
    now = datetime.now(UTC) - timedelta(minutes=1)
    event = FinancialTransactionEvent(
        transaction_id="tx-cai-20240315-091428-a89f",
        timestamp=now,
        account_id="acc-cai-91028374",
        merchant_id="mch-cai-hyperone-01",
        governorate=Governorate.CAIRO,
        channel=ChannelType.INSTAPAY,
        category=TransactionCategory.GROCERIES,
        amount_egp=Decimal("850.75"),
        status=TransactionStatus.COMPLETED,
        risk_score=0.025,
    )

    assert event.transaction_id == "tx-cai-20240315-091428-a89f"
    assert event.governorate == Governorate.CAIRO
    assert event.channel == ChannelType.INSTAPAY
    assert event.amount_egp == Decimal("850.75")
    assert event.source_type == SourceClassification.SYNTHETIC


def test_transaction_metadata_and_schema() -> None:
    meta = FinancialTransactionEvent.get_contract_metadata()
    assert meta.dataset_name == "financial_transactions"
    assert meta.domain == "retail_payments"
    assert meta.schema_version == SCHEMA_VERSION
    assert meta.source_classification == SourceClassification.SYNTHETIC

    schema = FinancialTransactionEvent.get_json_schema()
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["title"] == "financial_transactions"
    assert schema["x-source-classification"] == "synthetic"


def test_transaction_timestamp_prior_to_2000() -> None:
    with pytest.raises(ValidationError) as exc:
        FinancialTransactionEvent(
            transaction_id="tx-cai-19991231-0001",
            timestamp=datetime(1999, 12, 31, 23, 59, 59, tzinfo=UTC),
            account_id="acc-cai-91028374",
            merchant_id="mch-cai-hyperone-01",
            governorate=Governorate.CAIRO,
            channel=ChannelType.INSTAPAY,
            category=TransactionCategory.GROCERIES,
            amount_egp=Decimal("100.00"),
            status=TransactionStatus.COMPLETED,
            risk_score=0.01,
        )
    assert "cannot be prior to year 2000" in str(exc.value)


def test_transaction_timestamp_in_future() -> None:
    future_time = datetime.now(UTC) + timedelta(days=2)
    with pytest.raises(ValidationError) as exc:
        FinancialTransactionEvent(
            transaction_id="tx-cai-2099-0001",
            timestamp=future_time,
            account_id="acc-cai-91028374",
            merchant_id="mch-cai-hyperone-01",
            governorate=Governorate.CAIRO,
            channel=ChannelType.INSTAPAY,
            category=TransactionCategory.GROCERIES,
            amount_egp=Decimal("100.00"),
            status=TransactionStatus.COMPLETED,
            risk_score=0.01,
        )
    assert "cannot be in the future" in str(exc.value)


def test_transaction_invalid_amount_zero_or_negative() -> None:
    now = datetime.now(UTC) - timedelta(minutes=1)
    with pytest.raises(ValidationError):
        FinancialTransactionEvent(
            transaction_id="tx-cai-zero-amount",
            timestamp=now,
            account_id="acc-cai-91028374",
            merchant_id="mch-cai-hyperone-01",
            governorate=Governorate.CAIRO,
            channel=ChannelType.INSTAPAY,
            category=TransactionCategory.GROCERIES,
            amount_egp=Decimal("0.00"),
            status=TransactionStatus.COMPLETED,
            risk_score=0.01,
        )

    with pytest.raises(ValidationError):
        FinancialTransactionEvent(
            transaction_id="tx-cai-neg-amount",
            timestamp=now,
            account_id="acc-cai-91028374",
            merchant_id="mch-cai-hyperone-01",
            governorate=Governorate.CAIRO,
            channel=ChannelType.INSTAPAY,
            category=TransactionCategory.GROCERIES,
            amount_egp=Decimal("-50.00"),
            status=TransactionStatus.COMPLETED,
            risk_score=0.01,
        )


def test_transaction_invalid_risk_score() -> None:
    now = datetime.now(UTC) - timedelta(minutes=1)
    with pytest.raises(ValidationError):
        FinancialTransactionEvent(
            transaction_id="tx-cai-risk-high",
            timestamp=now,
            account_id="acc-cai-91028374",
            merchant_id="mch-cai-hyperone-01",
            governorate=Governorate.CAIRO,
            channel=ChannelType.INSTAPAY,
            category=TransactionCategory.GROCERIES,
            amount_egp=Decimal("100.00"),
            status=TransactionStatus.COMPLETED,
            risk_score=1.5,
        )

    with pytest.raises(ValidationError):
        FinancialTransactionEvent(
            transaction_id="tx-cai-risk-low",
            timestamp=now,
            account_id="acc-cai-91028374",
            merchant_id="mch-cai-hyperone-01",
            governorate=Governorate.CAIRO,
            channel=ChannelType.INSTAPAY,
            category=TransactionCategory.GROCERIES,
            amount_egp=Decimal("100.00"),
            status=TransactionStatus.COMPLETED,
            risk_score=-0.1,
        )


def test_transaction_forbid_extra_fields() -> None:
    now = datetime.now(UTC) - timedelta(minutes=1)
    with pytest.raises(ValidationError):
        FinancialTransactionEvent.model_validate(
            {
                "transaction_id": "tx-cai-valid-id-123",
                "timestamp": now.isoformat(),
                "account_id": "acc-99",
                "merchant_id": "mch-01",
                "governorate": "Cairo",
                "channel": "POS",
                "category": "Retail",
                "amount_egp": 150.0,
                "status": "COMPLETED",
                "risk_score": 0.1,
                "unauthorized_field": "injected_data",
            }
        )
