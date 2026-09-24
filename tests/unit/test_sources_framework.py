"""Unit tests for the EFIDP data sources framework and YAML configuration loader."""

from pathlib import Path
from typing import Any

import pytest

from efidp.contracts.enums import ConnectorType, SourceClassification
from efidp.core.exceptions import (
    ConfigurationError,
    ContractValidationError,
    DataQualityError,
    EFIDPError,
    SchemaVersionMismatchError,
    SourceConfigurationError,
)
from efidp.sources.api import APIDataSource
from efidp.sources.base import BaseDataSource
from efidp.sources.config import (
    SourceConfig,
    get_source_config,
    load_sources_config,
)
from efidp.sources.file import FileDataSource
from efidp.sources.mock import MockDataSource


def test_exception_hierarchy() -> None:
    assert issubclass(ContractValidationError, DataQualityError)
    assert issubclass(SchemaVersionMismatchError, ContractValidationError)
    assert issubclass(SourceConfigurationError, ConfigurationError)
    assert issubclass(SourceConfigurationError, EFIDPError)


def test_load_sources_config_valid() -> None:
    registry = load_sources_config()
    assert registry.version == "1.0"
    assert len(registry.sources) >= 4

    wb_src = get_source_config("world_bank_egypt")
    assert wb_src.connector_type == ConnectorType.API
    assert wb_src.source_type == SourceClassification.REAL_PUBLIC
    assert wb_src.endpoint is not None
    assert wb_src.retry_policy.max_retries == 3


def test_load_sources_config_file_not_found(tmp_path: Path) -> None:
    non_existent = tmp_path / "does_not_exist.yaml"
    with pytest.raises(SourceConfigurationError) as exc:
        load_sources_config(non_existent)
    assert "not found" in str(exc.value)


def test_load_sources_config_malformed_yaml(tmp_path: Path) -> None:
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("invalid: [yaml: broken", encoding="utf-8")
    with pytest.raises(SourceConfigurationError) as exc:
        load_sources_config(bad_yaml)
    assert "Failed to read sources YAML file" in str(exc.value)


def test_load_sources_config_invalid_root_type(tmp_path: Path) -> None:
    bad_yaml = tmp_path / "not_dict.yaml"
    bad_yaml.write_text("- item1\n- item2", encoding="utf-8")
    with pytest.raises(SourceConfigurationError) as exc:
        load_sources_config(bad_yaml)
    assert "must be a mapping" in str(exc.value)


def test_load_sources_config_validation_error(tmp_path: Path) -> None:
    bad_yaml = tmp_path / "invalid_schema.yaml"
    bad_yaml.write_text("version: '1.0'\nsources: []", encoding="utf-8")
    with pytest.raises(SourceConfigurationError) as exc:
        load_sources_config(bad_yaml)
    assert "schema validation failed" in str(exc.value)


def test_get_source_config_not_found() -> None:
    with pytest.raises(SourceConfigurationError) as exc:
        get_source_config("non_existent_source_id_xyz")
    assert "not found in registry" in str(exc.value)


def test_api_data_source() -> None:
    config = SourceConfig(
        source_id="test_api",
        source_name="Test API Source",
        source_type=SourceClassification.REAL_PUBLIC,
        dataset="economic_indicators",
        connector_type=ConnectorType.API,
        endpoint="https://api.worldbank.org/v2/country/EGY",
    )
    src = APIDataSource(config)
    assert src.validate_connection() is True
    assert src.source_id == "test_api"
    assert src.source_type == SourceClassification.REAL_PUBLIC

    schema = src.get_schema()
    assert schema["connector"] == "api"

    result = src.extract(sample_records=[{"key": "val"}])
    assert result.row_count == 1
    assert result.source_id == "test_api"

    # Test invalid URI endpoint
    bad_config = SourceConfig(
        source_id="test_bad_api",
        source_name="Bad API",
        source_type=SourceClassification.REAL_PUBLIC,
        dataset="economic_indicators",
        connector_type=ConnectorType.API,
        endpoint="ftp://invalid-scheme",
    )
    assert APIDataSource(bad_config).validate_connection() is False


def test_file_data_source(tmp_path: Path) -> None:
    test_json = tmp_path / "test_data.json"
    test_json.write_text('[{"indicator": "cpi", "val": 35.2}]', encoding="utf-8")

    config = SourceConfig(
        source_id="test_file",
        source_name="Test File Source",
        source_type=SourceClassification.REAL_PUBLIC,
        dataset="economic_indicators",
        connector_type=ConnectorType.FILE,
        path=str(test_json),
    )
    src = FileDataSource(config)
    assert src.validate_connection() is True

    schema = src.get_schema()
    assert schema["connector"] == "file"

    result = src.extract()
    assert result.row_count == 1
    assert result.records[0]["indicator"] == "cpi"

    # Test missing file path
    missing_config = SourceConfig(
        source_id="test_missing_file",
        source_name="Missing File",
        source_type=SourceClassification.REAL_PUBLIC,
        dataset="economic_indicators",
        connector_type=ConnectorType.FILE,
        path=str(tmp_path / "not_there.json"),
    )
    assert FileDataSource(missing_config).validate_connection() is False


def test_source_config_api_requires_endpoint() -> None:
    with pytest.raises(ValueError) as exc:
        SourceConfig.model_validate(
            {
                "source_id": "api_missing_endpoint",
                "source_name": "API Missing Endpoint",
                "source_type": "real_public",
                "dataset": "economic_indicators",
                "connector_type": "api",
                "endpoint": None,
            }
        )
    assert "endpoint is required when connector_type is 'api'" in str(exc.value)


def test_api_data_source_empty_endpoint() -> None:
    config = SourceConfig(
        source_id="mock_empty_ep",
        source_name="Mock API",
        source_type=SourceClassification.REAL_PUBLIC,
        dataset="economic_indicators",
        connector_type=ConnectorType.API,
        endpoint="https://valid-endpoint.com",
    )
    src = APIDataSource(config)
    src.endpoint = None
    assert src.validate_connection() is False


def test_file_data_source_empty_path_and_non_json(tmp_path: Path) -> None:
    config = SourceConfig(
        source_id="test_no_path",
        source_name="No Path File",
        source_type=SourceClassification.REAL_PUBLIC,
        dataset="economic_indicators",
        connector_type=ConnectorType.FILE,
        path=None,
    )
    src = FileDataSource(config)
    assert src.validate_connection() is False
    res_no_path = src.extract(sample_records=[{"empty": "path"}])
    assert res_no_path.row_count == 1

    # Test get_metadata
    meta = src.get_metadata()
    assert meta.source_id == "test_no_path"
    assert meta.connector_type == ConnectorType.FILE

    csv_file = tmp_path / "data.csv"
    csv_file.write_text("a,b\n1,2", encoding="utf-8")
    csv_config = SourceConfig(
        source_id="test_csv_file",
        source_name="CSV File",
        source_type=SourceClassification.REAL_PUBLIC,
        dataset="economic_indicators",
        connector_type=ConnectorType.FILE,
        path=str(csv_file),
    )
    csv_src = FileDataSource(csv_config)
    res = csv_src.extract(sample_records=[{"col1": "val1"}])
    assert res.row_count == 1
    assert res.records[0]["col1"] == "val1"


def test_base_data_source_not_implemented() -> None:
    config = SourceConfig(
        source_id="test_base",
        source_name="Base Source",
        source_type=SourceClassification.REAL_PUBLIC,
        dataset="economic_indicators",
        connector_type=ConnectorType.MOCK,
    )

    # Instantiate via a minimal subclass that provides dummy attributes to invoke base abstract methods
    class StubSource(BaseDataSource):
        def validate_connection(self) -> bool:
            return True

        def get_schema(self) -> dict[str, str]:
            return {}

        def extract(self, **kwargs: Any) -> Any:
            return None

    stub = StubSource(config)
    with pytest.raises(NotImplementedError):
        BaseDataSource.validate_connection(stub)
    with pytest.raises(NotImplementedError):
        BaseDataSource.get_schema(stub)
    with pytest.raises(NotImplementedError):
        BaseDataSource.extract(stub)


def test_mock_data_source() -> None:
    config = SourceConfig(
        source_id="test_mock",
        source_name="Test Mock Source",
        source_type=SourceClassification.SYNTHETIC,
        dataset="financial_transactions",
        connector_type=ConnectorType.MOCK,
    )
    mock_src = MockDataSource(config, mock_records=[{"tx": 1}])
    assert mock_src.validate_connection() is True

    mock_src.set_connection_status(False)
    assert mock_src.validate_connection() is False

    schema = mock_src.get_schema()
    assert schema["connector"] == "mock"
    assert schema["record_count"] == 1

    result = mock_src.extract()
    assert result.row_count == 1

    mock_src.set_mock_records([{"tx": 1}, {"tx": 2}])
    result2 = mock_src.extract()
    assert result2.row_count == 2
