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
- [x] **Phase 0:** Requirements, Data Strategy, and System Architecture Blueprint ([docs/architecture/phase-0-blueprint.md](docs/architecture/phase-0-blueprint.md))
- [x] **Phase 1:** Repository Foundation, Tooling, and Core Package (`src/efidp`)
- [x] **Phase 2:** Infrastructure & Local Docker Environment (PostgreSQL 16, MinIO, Kafka KRaft, Redis 7, Airflow 2.8, Prometheus, Grafana, Serving API)
- [x] **Phase 3:** Data Contracts & Source Framework (Pydantic v2 schemas, JSON Schema Draft 2020-12, declarative YAML source registry, structured validation engine)
- [ ] **Phase 4:** Raw Data Ingestion & Bronze Lake Storage (Upcoming)

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

## 4. Data Contracts & Extensible Source Framework (Phase 3)

The platform enforces contract-first data engineering using Pydantic v2 and JSON Schema Draft 2020-12.

- **Contracts Documentation**: [`docs/data-contracts.md`](docs/data-contracts.md)
- **Source Framework Documentation**: [`docs/source-framework.md`](docs/source-framework.md)

### Implemented Contracts (`src/efidp/contracts/`)
1. **Synthetic Financial Transactions (`synthetic_financial_transactions`, v1.0.0)**:
   Simulates Egyptian electronic retail payment rails (`InstaPay`, `POS`, `Mobile_Wallet`, `ATM`, `Web`) across the 27 Egyptian Governorates with strict EGP value boundaries and risk scores. Origin explicitly classified as `synthetic`.
2. **Macroeconomic Indicators (`macroeconomic_indicators`, v1.0.0)**:
   Macroeconomic time-series (inflation, GDP growth, interest rates) from CBE and World Bank supporting `ANNUAL`, `SEMI_ANNUAL`, `QUARTERLY`, `MONTHLY`, and `DAILY` observations. Origin classified as `real_public`.
3. **Market Observations (`market_data`, v1.0.0)**:
   Daily and intra-day EGX capital market session observations with cross-field price consistency checks (`high_price >= low_price`). Origin classified as `real_public`.
4. **Standard Ingestion Metadata Envelope (`ingestion_envelope_metadata`, v1.0.0)**:
   Standardized envelope wrapping batch payloads with lineage tracing (`ingestion_id`, `source_id`), SHA-256 payload integrity hashing, and extraction run durations. Origin classified as `derived`.

### Extensible Source Framework (`src/efidp/sources/`)
- Declarative source registry configured via [`config/sources.yaml`](config/sources.yaml).
- Abstract base connector (`BaseDataSource`) defining connection validation, schema introspection, and extraction interfaces.
- Implemented connectors: `APIDataSource`, `FileDataSource`, and `MockDataSource`.
- Automated test fixtures and machine-readable validation error reporting (`ContractValidator`).

For complete local development guidelines, refer to [docs/setup/development-setup.md](docs/setup/development-setup.md).
