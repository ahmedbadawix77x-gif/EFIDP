"""Data contract for Egyptian capital market observations and indices (EGX30, EGX70)."""

from datetime import date, timedelta
from typing import Literal

from pydantic import Field, field_validator, model_validator

from efidp.contracts.base import BaseDataContract, ContractMetadata
from efidp.contracts.enums import SourceClassification

SCHEMA_VERSION = "1.0.0"


class MarketObservationRecord(BaseDataContract):
    """Daily market observation and index snapshot contract (Egyptian Exchange EGX)."""

    asset_code: str = Field(
        ...,
        min_length=2,
        max_length=32,
        description="Ticker or index identifier (e.g., EGX30, EGX70, COMI)",
        examples=["EGX30"],
    )
    trading_date: date = Field(
        ...,
        description="Market trading session date",
        examples=[date(2024, 3, 10)],
    )
    close: float = Field(
        ...,
        gt=0.0,
        description="Mandatory session closing index/price value. Must be strictly positive.",
        examples=[28540.25],
    )
    open: float | None = Field(
        default=None,
        gt=0.0,
        description="Optional session opening index/price value",
        examples=[28100.50],
    )
    high: float | None = Field(
        default=None,
        gt=0.0,
        description="Optional intra-session high value",
        examples=[28650.00],
    )
    low: float | None = Field(
        default=None,
        gt=0.0,
        description="Optional intra-session low value",
        examples=[28050.10],
    )
    volume: int | None = Field(
        default=None,
        ge=0,
        description="Optional total executed share/contract trade count",
        examples=[145200300],
    )
    turnover: float | None = Field(
        default=None,
        ge=0.0,
        description="Optional total transaction value / turnover in EGP",
        examples=[3250100450.0],
    )
    source_type: Literal[SourceClassification.REAL_PUBLIC] = Field(
        default=SourceClassification.REAL_PUBLIC,
        description="Origin classification marking this data as verified public market data",
    )

    @field_validator("trading_date")
    @classmethod
    def validate_date_not_in_future(cls, v: date) -> date:
        """Ensure market observation trading date is not in the future."""
        max_allowed = date.today() + timedelta(days=1)
        if v > max_allowed:
            raise ValueError(f"Trading date {v.isoformat()} cannot be in the future")
        return v

    @model_validator(mode="after")
    def validate_ohlc_consistency(self) -> "MarketObservationRecord":
        """Enforce financial price boundary consistency across Open, High, Low, and Close."""
        if self.high is not None and self.low is not None and self.high < self.low:
            raise ValueError(
                f"Session high ({self.high}) cannot be lower than session low ({self.low})"
            )

        if self.high is not None:
            if self.open is not None and self.high < self.open:
                raise ValueError(
                    f"Session high ({self.high}) cannot be lower than open ({self.open})"
                )
            if self.high < self.close:
                raise ValueError(
                    f"Session high ({self.high}) cannot be lower than close ({self.close})"
                )

        if self.low is not None:
            if self.open is not None and self.low > self.open:
                raise ValueError(
                    f"Session low ({self.low}) cannot be higher than open ({self.open})"
                )
            if self.low > self.close:
                raise ValueError(
                    f"Session low ({self.low}) cannot be higher than close ({self.close})"
                )

        return self

    @classmethod
    def get_contract_metadata(cls) -> ContractMetadata:
        """Return formal contract metadata."""
        return ContractMetadata(
            dataset_name="daily_market",
            domain="capital_markets",
            schema_version=SCHEMA_VERSION,
            source_classification=SourceClassification.REAL_PUBLIC,
            description=(
                "Daily trading session indices and price observations for the Egyptian Exchange (EGX). "
                "Defines mandatory close price and optional OHLCV statistics."
            ),
        )
