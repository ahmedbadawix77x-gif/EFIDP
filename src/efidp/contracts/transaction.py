"""Data contract for synthetic financial transaction events in the Egyptian retail market."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Literal

from pydantic import Field, field_validator

from efidp.contracts.base import BaseDataContract, ContractMetadata
from efidp.contracts.enums import (
    ChannelType,
    Governorate,
    SourceClassification,
    TransactionCategory,
    TransactionStatus,
)

SCHEMA_VERSION = "1.0.0"


class FinancialTransactionEvent(BaseDataContract):
    """Synthetic retail financial transaction event contract (Egyptian Market Context).

    DISCLAIMER: This dataset represents synthetic simulated transactions modeled after
    Egyptian retail payment behaviors (InstaPay, Mobile Wallets, POS, ATM).
    It contains NO actual banking records or real customer PII.
    """

    transaction_id: str = Field(
        ...,
        min_length=8,
        max_length=64,
        description="Unique identifier for the financial transaction event",
        examples=["tx-cai-2024-001928374"],
    )
    timestamp: datetime = Field(
        ...,
        description="UTC timestamp when the transaction occurred. Must be >= 2000-01-01 and not in the future.",
    )
    account_id: str = Field(
        ...,
        min_length=4,
        max_length=64,
        description="Pseudonymous synthetic customer account identifier",
        examples=["acc-99210-eg"],
    )
    merchant_id: str = Field(
        ...,
        min_length=4,
        max_length=64,
        description="Synthetic merchant or terminal identifier",
        examples=["mch-cai-hyper-01"],
    )
    governorate: Governorate = Field(
        ...,
        description="Egyptian governorate where the payment or terminal interaction took place",
    )
    channel: ChannelType = Field(
        ...,
        description="Payment channel used (e.g. InstaPay, POS, Mobile_Wallet, ATM, Web)",
    )
    category: TransactionCategory = Field(
        ...,
        description="Merchant spending category (e.g. Retail, Groceries, Utilities)",
    )
    amount_egp: Decimal = Field(
        ...,
        gt=Decimal("0.00"),
        decimal_places=2,
        max_digits=12,
        description="Transaction amount in Egyptian Pounds (EGP). Must be strictly positive.",
        examples=[Decimal("249.50")],
    )
    status: TransactionStatus = Field(
        ...,
        description="Execution status of the transaction event",
    )
    risk_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Computed transaction risk probability score between 0.0 (clean) and 1.0 (fraud)",
        examples=[0.042],
    )
    source_type: Literal[SourceClassification.SYNTHETIC] = Field(
        default=SourceClassification.SYNTHETIC,
        description="Explicit origin classification marking this data as synthetic simulation",
    )

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp_bounds(cls, v: datetime) -> datetime:
        """Ensure timestamp is not in the future and occurred on or after year 2000."""
        # Normalize timezone awareness for comparison
        ts_utc = v if v.tzinfo is not None else v.replace(tzinfo=UTC)
        min_allowed = datetime(2000, 1, 1, 0, 0, 0, tzinfo=UTC)
        # Allow 5 minutes clock skew tolerance
        max_allowed = datetime.now(UTC) + timedelta(minutes=5)

        if ts_utc < min_allowed:
            raise ValueError(f"Timestamp {v.isoformat()} cannot be prior to year 2000")
        if ts_utc > max_allowed:
            raise ValueError(f"Timestamp {v.isoformat()} cannot be in the future")
        return v

    @classmethod
    def get_contract_metadata(cls) -> ContractMetadata:
        """Return formal contract metadata."""
        return ContractMetadata(
            dataset_name="financial_transactions",
            domain="retail_payments",
            schema_version=SCHEMA_VERSION,
            source_classification=SourceClassification.SYNTHETIC,
            description=(
                "Synthetic retail financial transaction events across Egyptian payment channels "
                "(InstaPay, Mobile Wallet, POS, ATM). For simulation and analytics testing only."
            ),
        )
