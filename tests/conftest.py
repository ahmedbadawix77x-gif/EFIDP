"""Shared pytest test configuration and fixtures."""

import os
from collections.abc import Generator

import pytest

from efidp.core.config import PlatformSettings, get_settings


@pytest.fixture(autouse=True)
def clean_env() -> Generator[None, None, None]:
    """Ensure environment is isolated between tests and cache is cleared."""
    get_settings.cache_clear()
    old_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(old_env)
    get_settings.cache_clear()


@pytest.fixture
def test_settings() -> PlatformSettings:
    """Return a fresh PlatformSettings instance for testing."""
    return PlatformSettings(
        environment="testing",
        debug=True,
        log_level="DEBUG",
        log_format="console",
    )
