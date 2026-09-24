# EFIDP — Local Development & Tooling Guide

This document outlines the local setup, developer tooling, and code quality workflows for the **Egypt Financial Intelligence Data Platform (EFIDP)**.

---

## 1. Prerequisites

- **Python:** 3.11.x (Strictly recommended for full compatibility with PySpark, Apache Airflow, and Kafka clients)
- **Git:** 2.40+
- **Docker & Docker Compose:** Docker Desktop with Compose v2+
- **PowerShell (Windows)** or **Bash (Linux/macOS)**

---

## 2. Initial Setup

### 2.1 Clone and Environment Initialization
```bash
# Clone the repository
git clone https://github.com/your-org/efidp-platform.git
cd efidp-platform

# Initialize Python 3.11 virtual environment
py -3.11 -m venv .venv

# Activate the virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate
```

### 2.2 Install Dependencies & Pre-commit Hooks
```bash
# Upgrade pip and install package in editable mode with development dependencies
pip install --upgrade pip
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 2.3 Configure Environment Variables
```bash
# Copy the environment template
cp .env.example .env
```
Inspect `.env` and configure local ports or overrides if default ports clash with existing local services.

---

## 3. Developer Tooling & Quality Gates

EFIDP enforces strict code formatting, linting, type checks, and test coverage before any code is committed.

### 3.1 Code Quality Commands

| Check / Task | Tool | Windows PowerShell | Linux / macOS (Makefile) |
|:---|:---|:---|:---|
| **Linting** | Ruff | `.\scripts\dev.ps1 lint` | `make lint` |
| **Format Check** | Ruff | `.\scripts\dev.ps1 format` | `make format` |
| **Auto-Fix Format & Lint** | Ruff | `.\scripts\dev.ps1 format-fix` | `make format-fix` |
| **Type Checking** | MyPy (strict) | `.\scripts\dev.ps1 typecheck` | `make typecheck` |
| **Unit Tests** | Pytest | `.\scripts\dev.ps1 test` | `make test` |
| **Test Coverage** | Pytest-cov | `.\scripts\dev.ps1 test-cov` | `make test-cov` |
| **Full Quality Gate** | All Tools | `.\scripts\dev.ps1 check` | `make check` |

---

## 4. Configuration Architecture

The platform uses **Pydantic Settings v2** (`efidp.core.config.PlatformSettings`) for strongly-typed, environment-aware configuration.

- Connection strings and credentials are dynamically constructed without hardcoding.
- Settings are validated at import/instantiation time.
- All secrets are loaded from environment variables or `.env`.

Example usage in application modules:
```python
from efidp.core.config import get_settings

settings = get_settings()
print(settings.postgres.sync_dsn)
print(settings.minio.endpoint_url)
```

---

## 5. Structured Logging Foundation

EFIDP uses `structlog` to output structured JSON events in production/observability pipelines and human-readable colored logs during local debugging:

```python
from efidp.core.logging import configure_logging, get_logger

# Initialize platform logging once at startup
configure_logging()

# Bind contextual metadata
logger = get_logger("ingestion.cbe", source_id="cbe_inflation")
logger.info("batch_extracted", row_count=120, status="SUCCESS")
```

Output format (JSON):
```json
{
  "timestamp": "2026-09-24T06:00:00.000Z",
  "level": "info",
  "logger": "ingestion.cbe",
  "event": "batch_extracted",
  "source_id": "cbe_inflation",
  "row_count": 120,
  "status": "SUCCESS"
}
```
