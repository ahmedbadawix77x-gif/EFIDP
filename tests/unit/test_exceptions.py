"""Unit tests for efidp.core.exceptions module."""

from efidp.core.exceptions import (
    ConfigurationError,
    DataQualityError,
    EFIDPError,
    IngestionError,
    StorageError,
)


def test_base_exception_formatting() -> None:
    """Verify base exception message and details dictionary formatting."""
    err_simple = EFIDPError("Something went wrong")
    assert str(err_simple) == "Something went wrong"
    assert err_simple.details == {}

    err_detailed = EFIDPError("Invalid metric", details={"metric": "inflation", "value": -5})
    assert "Invalid metric" in str(err_detailed)
    assert "inflation" in str(err_detailed)
    assert err_detailed.details["value"] == -5


def test_subclass_hierarchy() -> None:
    """Verify exception subclasses inherit from EFIDPError."""
    assert issubclass(ConfigurationError, EFIDPError)
    assert issubclass(IngestionError, EFIDPError)
    assert issubclass(DataQualityError, EFIDPError)
    assert issubclass(StorageError, EFIDPError)
