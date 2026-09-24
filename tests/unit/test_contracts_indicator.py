"""Unit tests for EconomicIndicatorRecord contract."""

from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from efidp.contracts.enums import Frequency, SourceClassification
from efidp.contracts.indicator import SCHEMA_VERSION, EconomicIndicatorRecord


def test_valid_economic_indicator() -> None:
    rec = EconomicIndicatorRecord(
        indicator_code="FP.CPI.TOTL.ZG",
        observation_date=date(2024, 1, 1),
        value=35.7,
        previous_value=33.2,
        unit="%",
        source="Central Bank of Egypt",
        frequency=Frequency.MONTHLY,
        metadata={"revision": 1},
    )

    assert rec.indicator_code == "FP.CPI.TOTL.ZG"
    assert rec.value == 35.7
    assert rec.previous_value == 33.2
    assert rec.frequency == Frequency.MONTHLY
    assert rec.source_type == SourceClassification.REAL_PUBLIC
    assert rec.metadata == {"revision": 1}


def test_indicator_metadata_and_schema() -> None:
    meta = EconomicIndicatorRecord.get_contract_metadata()
    assert meta.dataset_name == "economic_indicators"
    assert meta.domain == "macroeconomics"
    assert meta.schema_version == SCHEMA_VERSION
    assert meta.source_classification == SourceClassification.REAL_PUBLIC

    schema = EconomicIndicatorRecord.get_json_schema()
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["title"] == "economic_indicators"


def test_indicator_future_observation_date() -> None:
    future_date = date.today() + timedelta(days=30)
    with pytest.raises(ValidationError) as exc:
        EconomicIndicatorRecord(
            indicator_code="CBE_CORRIDOR_LENDING",
            observation_date=future_date,
            value=27.25,
            unit="%",
            source="Central Bank of Egypt",
            frequency=Frequency.MONTHLY,
        )
    assert "cannot be in the future" in str(exc.value)


def test_indicator_missing_required_fields() -> None:
    with pytest.raises(ValidationError):
        EconomicIndicatorRecord.model_validate(
            {
                "indicator_code": "CPI",
                # missing observation_date
                "value": 10.5,
                "unit": "%",
                "source": "World Bank",
                "frequency": "MONTHLY",
            }
        )
