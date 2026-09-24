# EFIDP Data Source Framework & Configuration

**Platform Component**: Extensible Source Framework (`src/efidp/sources/`)  
**Registry Configuration**: `config/sources.yaml`  
**Implementation Phase**: Phase 3 (Foundation for Phase 4 Ingestion)

---

## 1. Architectural Overview

The **EFIDP Source Framework** provides a configuration-driven, decoupled abstraction layer for acquiring data from diverse external protocols (REST APIs, Local/S3 Files, Message Queues, Synthetic Generators) without binding pipeline code to specific network protocols or vendor SDKs.

```
+-----------------------------------------------------------------------------------+
|                           YAML SOURCE REGISTRY (config/sources.yaml)              |
|         (Metadata, Connector Type, Endpoints, Retry Policies, Cron Schedules)    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        PYDANTIC SOURCE CONFIGURATION LAYER                        |
|                     (SourceConfig, RetryPolicy, SourcesRegistry)                  |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                            BASE DATA SOURCE ABSTRACTION                           |
|                               (BaseDataSource [ABC])                              |
|           +--------------------+--------------------+--------------------+        |
|           |                    |                    |                    |        |
|           v                    v                    v                    v        |
|     APIDataSource        FileDataSource       MockDataSource      StreamingSource |
|      (HTTP/REST)       (Local JSON / S3)     (Test Generators)      (Future/v2)   |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                               EXTRACTION RESULT                                   |
|             (ExtractionResult: source_id, records, row_count, timing)             |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                              PHASE 4 CONSUMPTION                                  |
|         (Validation Engine -> Metadata Envelope -> MinIO Bronze Lake Storage)     |
+-----------------------------------------------------------------------------------+
```

---

## 2. Core Abstractions (`src/efidp/sources/base.py`)

Every connector inherits from [`BaseDataSource`](file:///e:/Progects/efidp-platform/src/efidp/sources/base.py), implementing a standard lifecycle:

```python
class BaseDataSource(ABC):
    def __init__(self, config: SourceConfig) -> None:
        self.config = config

    @abstractmethod
    def validate_connection(self) -> bool:
        """Validate network, endpoint, file, or credential accessibility."""
        pass

    @abstractmethod
    def get_schema(self) -> dict[str, Any]:
        """Return the target contract schema or raw data schema definition."""
        pass

    @abstractmethod
    def extract(self, **kwargs: Any) -> ExtractionResult:
        """Execute the ingestion extraction step, returning an ExtractionResult."""
        pass

    def get_metadata(self) -> SourceMetadata:
        """Return source configuration metadata."""
        pass
```

### Connector Implementations

1. **[`APIDataSource`](file:///e:/Progects/efidp-platform/src/efidp/sources/api.py)**:
   - Designed for external REST/HTTP endpoints (e.g. World Bank API, CBE Open Data).
   - Validates URL syntax, HTTP protocol headers, and health endpoint accessibility.
2. **[`FileDataSource`](file:///e:/Progects/efidp-platform/src/efidp/sources/file.py)**:
   - Designed for seed files, historical batch dumps, and object store manifests (JSON, NDJSON, Parquet).
   - Validates file existence, read permissions, and schema alignment.
3. **[`MockDataSource`](file:///e:/Progects/efidp-platform/src/efidp/sources/mock.py)**:
   - Built for deterministic unit tests and synthetic event generation pipelines without external dependencies.

---

## 3. Configuration-Driven Source Registry (`config/sources.yaml`)

Sources are declared in `config/sources.yaml` and loaded via [`load_sources_config()`](file:///e:/Progects/efidp-platform/src/efidp/sources/config.py):

```yaml
version: "1.0"

sources:
  - source_id: "world_bank_egypt"
    source_name: "World Bank Open Data API (Egypt Indicators)"
    source_type: "real_public"
    dataset: "economic_indicators"
    schema_version: "1.0.0"
    connector_type: "api"
    endpoint: "http://api.worldbank.org/v2/country/EGY/indicator"
    enabled: true
    retry_policy:
      max_retries: 3
      backoff_factor: 2.0
      timeout_seconds: 30.0
    schedule_cron: "0 2 1 * *"

  - source_id: "synthetic_fin_transactions"
    source_name: "Egypt Synthetic Retail Payment Generator"
    source_type: "synthetic"
    dataset: "financial_transactions"
    schema_version: "1.0.0"
    connector_type: "mock"
    enabled: true
    retry_policy:
      max_retries: 1
      backoff_factor: 1.0
      timeout_seconds: 5.0
```

### Source Origin Classifications

| Classification | Meaning | Quality Expectation | Example Source |
| :--- | :--- | :--- | :--- |
| `real_public` | Real-world public institution or regulatory data | Uncontrolled upstream, strict schema validation | World Bank, CBE, EGX |
| `synthetic` | Generated for testing, load simulation, or research | Strictly adheres to domain parameters | Synthetic payment rail events |
| `derived` | Computed/aggregated from other internal datasets | Deterministic, downstream pipeline dependencies | Feature store, rolling metrics |

---

## 4. Usage Pattern

```python
from efidp.sources.config import get_source_config
from efidp.sources.api import APIDataSource
from efidp.contracts.validator import ContractValidator
from efidp.contracts.indicator import EconomicIndicatorContract

# 1. Load declarative configuration
config = get_source_config("world_bank_egypt")

# 2. Instantiate connector
connector = APIDataSource(config)

# 3. Validate connectivity
if not connector.validate_connection():
    raise RuntimeError(f"Cannot reach source: {config.source_id}")

# 4. Extract data
extraction = connector.extract()

# 5. Validate records against data contract
validation_result = ContractValidator.validate_batch(EconomicIndicatorContract, extraction.records)
```

---

## 5. Phase 4 Roadmap & Non-Goals for Phase 3

- **Phase 3 Boundary**:
  - Implements abstract interfaces, declarative configurations, validation utilities, and mock connectors.
  - Does NOT implement live network HTTP extraction loops, database writes, or Airflow DAG execution.
- **Phase 4 Implementation**:
  - Full HTTP request sessions with rate-limiting, proxies, and auth headers.
  - Streaming connectors for real-time Kafka topics.
  - Automated Bronze object storage writers with partition management.
