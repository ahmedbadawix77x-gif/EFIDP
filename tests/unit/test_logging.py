"""Unit tests for efidp.core.logging module."""

import logging

import pytest

from efidp.core.config import PlatformSettings
from efidp.core.logging import configure_logging, get_logger


def test_configure_logging_json(caplog: pytest.LogCaptureFixture) -> None:
    """Verify logging configuration with JSON format."""
    settings = PlatformSettings(log_level="DEBUG", log_format="json")
    configure_logging(settings)

    logger = get_logger("test_json")
    with caplog.at_level(logging.INFO):
        logger.info("system_boot", component="kernel", version="0.1.0")

    assert logging.getLogger().level == logging.DEBUG


def test_configure_logging_console(caplog: pytest.LogCaptureFixture) -> None:
    """Verify logging configuration with console format."""
    settings = PlatformSettings(log_level="INFO", log_format="console")
    configure_logging(settings)

    logger = get_logger("test_console")
    with caplog.at_level(logging.INFO):
        logger.info("service_ready", port=8000)

    assert logging.getLogger().level == logging.INFO


def test_configure_logging_default() -> None:
    """Verify configure_logging initializes with default settings when none provided."""
    configure_logging()
    logger = get_logger("test_default")
    assert logger is not None


def test_logger_bind() -> None:
    """Verify context variable binding on logger instance."""
    logger = get_logger("test_bound", service="ingestion-worker")
    bound = logger.bind(job_id="job-12345")
    assert bound is not None
