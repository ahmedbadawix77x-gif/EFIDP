# EFIDP — Egypt Financial Intelligence Data Platform

[![CI Validation](https://github.com/your-org/efidp-platform/actions/workflows/pr-validation.yml/badge.svg)](https://github.com/your-org/efidp-platform/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3119/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](http://mypy-lang.org/)

EFIDP is an enterprise-grade financial data engineering and macroeconomic analytics platform simulating how modern organizations collect, validate, process, store, analyze, serve, monitor, and govern financial and economic data in Egypt.

---

## 1. Project Overview & Architecture Blueprint

The complete system specification, architecture proposal, and 23-phase engineering roadmap are documented in:
👉 [docs/architecture/phase-0-blueprint.md](docs/architecture/phase-0-blueprint.md)

### Current Status
- [x] **Phase 0:** Requirements, Data Strategy, and System Architecture Blueprint
- [x] **Phase 1:** Repository Foundation, Tooling, and Core Package (`src/efidp`)
- [ ] **Phase 2:** Infrastructure & Local Docker Environment (MinIO, Postgres, Kafka, Airflow)
- [ ] **Phase 3:** Data Contracts & Source Framework

---

## 2. Quickstart for Developers

### Prerequisites
- Python 3.11.x
- Git

### Setup
```bash
# Clone and enter the repository
git clone https://github.com/your-org/efidp-platform.git
cd efidp-platform

# Create and activate virtual environment
py -3.11 -m venv .venv
.venv\Scripts\activate   # Linux/macOS: source .venv/bin/activate

# Install package in editable mode with dev dependencies
pip install -e ".[dev]"

# Copy environment configuration
cp .env.example .env
```

### Running Quality Checks
```bash
# Windows PowerShell:
.\scripts\dev.ps1 check

# Linux/macOS:
make check
```

---

## 3. Repository Structure

```
efidp-platform/
├── apps/               # Serving API, Ingestion CLI, and Streaming workers
├── config/             # Declarative pipeline & source registry YAML configs
├── data/               # Contracts (JSON Schema), sample fixtures, and seed data
├── docs/               # System architecture, ADRs, data dictionary, and runbooks
├── infrastructure/     # Dockerfiles, Prometheus, Grafana, and MinIO scripts
├── metadata/           # Data audit, lineage, and pipeline metastore
├── pipelines/          # Apache Airflow DAGs and orchestration
├── quality/            # Great Expectations suites and custom validation rules
├── scripts/            # Developer automation and benchmark scripts
├── src/                # Shared platform package (efidp.core)
├── tests/              # Unit, integration, contract, API, and stream tests
├── transformations/    # Medallion processing (Bronze -> Silver -> Gold)
├── warehouse/          # Star schema DDL models and migrations
├── .env.example        # Environment variable specification template
├── Makefile            # POSIX developer workflows
├── pyproject.toml      # Project dependencies and tool configurations
└── README.md
```

For complete local development guidelines, refer to [docs/setup/development-setup.md](docs/setup/development-setup.md).
