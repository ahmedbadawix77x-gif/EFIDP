"""Data contract for macroeconomic and economic indicator time-series observations."""

from datetime import date, timedelta
from typing import Any, Literal

from pydantic import Field, field_validator

from efidp.contracts.base import BaseDataContract, ContractMetadata
from efidp.contracts.enums import Frequency, SourceClassification

SCHEMA_VERSION = "1.0.0"


class EconomicIndicatorRecord(BaseDataContract):
    """Macroeconomic indicator observation contract (World Bank, Central Bank of Egypt, etc.)."""

    indicator_code: str = Field(
        ...,
        min_length=2,
        max_length=64,
        description="Standardized code identifying the economic indicator",
        examples=["FP.CPI.TOTL.ZG", "CBE_CORRIDOR_LENDING", "USD_EGP_BUY"],
    )
    observation_date: date = Field(
        ...,
        description="Reference observation date for the statistical measurement",
        examples=[date(2024, 1, 1)],
    )
    value: float = Field(
        ...,
        description="Observed numeric value of the indicator",
        examples=[35.7],
    )
    previous_value: float | None = Field(
        default=None,
        description="Previous period observed value where available for delta calculation",
        examples=[33.2],
    )
    unit: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="Unit of measurement (e.g., %, EGP, USD, Index Points)",
        examples=["%"],
    )
    source: str = Field(
        ...,
        min_length=2,
        max_length=128,
        description="Publishing authority or institution (e.g., Central Bank of Egypt, World Bank)",
        examples=["Central Bank of Egypt"],
    )
    frequency: Frequency = Field(
        ...,
        description="Reporting frequency (ANNUAL, SEMI_ANNUAL, QUARTERLY, MONTHLY, DAILY)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Supplementary contextual metadata, notes, or raw API response fragments",
    )
    source_type: Literal[SourceClassification.REAL_PUBLIC] = Field(
        default=SourceClassification.REAL_PUBLIC,
        description="Origin classification marking this data as verified public statistics",
    )

    @field_validator("observation_date")
    @classmethod
    def validate_date_not_far_future(cls, v: date) -> date:
        """Ensure observation date is not unreasonably in the future."""
        max_allowed = date.today() + timedelta(days=1)
        if v > max_allowed:
            raise ValueError(f"Observation date {v.isoformat()} cannot be in the future")
        return v

    @classmethod
    def get_contract_metadata(cls) -> ContractMetadata:
        """Return formal contract metadata."""
        return ContractMetadata(
            dataset_name="economic_indicators",
            domain="macroeconomics",
            schema_version=SCHEMA_VERSION,
            source_classification=SourceClassification.REAL_PUBLIC,
            description=(
                "Macroeconomic indicators tracking Egyptian inflation, interest rates, GDP, "
                "and financial statistics published by authoritative official bodies."
            ),
        )
