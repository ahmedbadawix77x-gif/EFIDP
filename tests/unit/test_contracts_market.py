"""Unit tests for MarketObservationRecord contract."""

from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from efidp.contracts.enums import SourceClassification
from efidp.contracts.market import SCHEMA_VERSION, MarketObservationRecord


def test_valid_minimal_market_record() -> None:
    rec = MarketObservationRecord(
        asset_code="EGX30",
        trading_date=date(2024, 3, 10),
        close=28540.25,
    )
    assert rec.asset_code == "EGX30"
    assert rec.close == 28540.25
    assert rec.open is None
    assert rec.source_type == SourceClassification.REAL_PUBLIC


def test_valid_full_market_record() -> None:
    rec = MarketObservationRecord(
        asset_code="EGX30",
        trading_date=date(2024, 3, 10),
        close=28540.25,
        open=28100.50,
        high=28650.00,
        low=28050.10,
        volume=145200300,
        turnover=3250100450.0,
    )
    assert rec.high == 28650.00
    assert rec.low == 28050.10
    assert rec.volume == 145200300


def test_market_metadata_and_schema() -> None:
    meta = MarketObservationRecord.get_contract_metadata()
    assert meta.dataset_name == "daily_market"
    assert meta.domain == "capital_markets"
    assert meta.schema_version == SCHEMA_VERSION

    schema = MarketObservationRecord.get_json_schema()
    assert schema["title"] == "daily_market"


def test_market_future_trading_date() -> None:
    future_date = date.today() + timedelta(days=10)
    with pytest.raises(ValidationError) as exc:
        MarketObservationRecord(
            asset_code="EGX30",
            trading_date=future_date,
            close=28000.0,
        )
    assert "cannot be in the future" in str(exc.value)


def test_market_high_lower_than_low() -> None:
    with pytest.raises(ValidationError) as exc:
        MarketObservationRecord(
            asset_code="EGX30",
            trading_date=date(2024, 3, 10),
            close=28500.0,
            high=28000.0,
            low=28600.0,
        )
    assert "cannot be lower than session low" in str(exc.value)


def test_market_high_lower_than_close_or_open() -> None:
    with pytest.raises(ValidationError) as exc:
        MarketObservationRecord(
            asset_code="EGX30",
            trading_date=date(2024, 3, 10),
            open=28700.0,
            close=28500.0,
            high=28600.0,
            low=28400.0,
        )
    assert "cannot be lower than open" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        MarketObservationRecord(
            asset_code="EGX30",
            trading_date=date(2024, 3, 10),
            open=28450.0,
            close=28700.0,
            high=28600.0,
            low=28400.0,
        )
    assert "cannot be lower than close" in str(exc.value)


def test_market_low_higher_than_close_or_open() -> None:
    with pytest.raises(ValidationError) as exc:
        MarketObservationRecord(
            asset_code="EGX30",
            trading_date=date(2024, 3, 10),
            open=28200.0,
            close=28500.0,
            high=28600.0,
            low=28300.0,
        )
    assert "cannot be higher than open" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        MarketObservationRecord(
            asset_code="EGX30",
            trading_date=date(2024, 3, 10),
            open=28400.0,
            close=28200.0,
            high=28600.0,
            low=28300.0,
        )
    assert "cannot be higher than close" in str(exc.value)
