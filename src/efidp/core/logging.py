"""Structured logging subsystem for the EFIDP platform.

Provides JSON formatted logs for production/observability and colored console output
for local development, powered by structlog.
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import FilteringBoundLogger, Processor

from efidp.core.config import PlatformSettings, get_settings


def configure_logging(settings: PlatformSettings | None = None) -> None:
    """Configure structured logging processors and standard library routing."""
    if settings is None:
        settings = get_settings()

    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if settings.log_format == "json":
        renderer: Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)


def get_logger(name: str | None = None, **initial_values: Any) -> FilteringBoundLogger:
    """Get a structured contextual logger instance."""
    logger: FilteringBoundLogger = structlog.get_logger(name)
    if initial_values:
        logger = logger.bind(**initial_values)
    return logger
