# EFIDP Data Contracts & Schema Specification

**Platform Component**: Data Contracts Architecture (`src/efidp/contracts/`)  
**Specification Version**: `1.0.0`  
**Schema Standard**: JSON Schema (Draft 2020-12) / Pydantic v2  
**Implementation Phase**: Phase 3 (Foundation for Phase 4 Ingestion)

---

## 1. Architectural Overview

Data contracts in the **Egypt Financial Intelligence Data Platform (EFIDP)** define formal, bidirectional agreements between upstream data producers and downstream analytical consumers. Rather than allowing raw, unchecked data to traverse pipeline boundaries, every record must conform to an explicit contract schema before entering Bronze storage or message buses.

```
+-----------------------------------------------------------------------------------+
|                                  EFIDP SOURCE                                     |
|           (Real Public APIs, Synthetic Generators, Batch File Dumps)              |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        CONTRACT VALIDATION ENGINE (Phase 3)                       |
|   +---------------------------------------------------------------------------+   |
|   |  Pydantic v2 Strict Enforcement (extra="forbid", whitespace stripped)     |   |
|   |  Domain Boundary Validation (EGP caps, risk scores, governorate enums)    |   |
|   |  Standard Ingestion Metadata Envelope (SHA-256 payload hash verification) |   |
|   +---------------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------------+
                                   /           \
                     (Valid Records)           (Validation Failures)
                                 /               \
                                v                 v
             +-----------------------+       +-------------------------------+
             | Phase 4 Ingestion     |       | Dead Letter Queue / Quarantine|
             | Bronze Lake Storage   |       | Machine-Readable Error Report |
             +-----------------------+       +-------------------------------+
```

### Core Design Principles

1. **Strict Type Safety & Boundary Guards**: All contracts inherit from [`BaseDataContract`](file:///e:/Progects/efidp-platform/src/efidp/contracts/base.py) with `extra="forbid"`, preventing accidental field leakage, silent schema drift, or unrecognized properties.
2. **Explicit Origin Classification**: Every contract and payload requires an explicit [`SourceClassification`](file:///e:/Progects/efidp-platform/src/efidp/contracts/enums.py) (`real_public`, `synthetic`, or `derived`). Synthetic banking transaction events are explicitly flagged as `synthetic`, ensuring they are never conflated with real regulatory data.
3. **Decoupled JSON Schema Export**: Pydantic models automatically export draft 2020-12 compliant JSON Schema artifacts (`data/contracts/*.schema.json`), enabling non-Python consumers (Spark, Rust, Presto, frontend clients) to validate records independently.
4. **Machine-Readable Validation Outcomes**: Validation failures return structured [`ValidationErrorDetail`](file:///e:/Progects/efidp-platform/src/efidp/contracts/validator.py) objects detailing exact field paths, error classifications, human-readable explanations, and rejected input values.
5. **Standardized Ingestion Envelope**: Payloads are wrapped in an [`IngestionEnvelope`](file:///e:/Progects/efidp-platform/src/efidp/contracts/envelope.py) preserving cryptographic lineage (SHA-256 hash), row counts, extraction durations, and pipeline identifiers.

---

## 2. Core Contracts Specification

### 2.1 Synthetic Financial Transactions Contract

- **Dataset Identifier**: `synthetic_financial_transactions`
- **Domain**: `financial_services`
- **Schema Version**: `1.0.0`
- **Source Classification**: `synthetic`
- **Implementation**: [`FinancialTransactionContract`](file:///e:/Progects/efidp-platform/src/efidp/contracts/transaction.py)
- **JSON Schema Path**: `data/contracts/transaction.schema.json`

Simulates retail electronic payment events across Egyptian payment rails (InstaPay, POS, Mobile Wallets, ATMs, Web).

#### Field Definitions & Constraints

| Field | Type | Required | Constraints | Semantic Description |
| :--- | :--- | :--- | :--- | :--- |
| `transaction_id` | `UUID4` | Yes | Non-null, RFC 4122 standard | Unique identifier of the transaction event |
| `timestamp` | `datetime` | Yes | UTC, >= 2000-01-01, <= now + 5 min | Event occurrence timestamp |
| `account_id` | `str` | Yes | Min length: 6, max length: 32 | Obfuscated account identifier |
| `merchant_id` | `str` | Yes | Min length: 4, max length: 32 | Merchant or recipient terminal identifier |
| `governorate` | `Governorate` | Yes | One of 27 Egyptian Governorates | Geographic location of transaction execution |
| `channel` | `ChannelType` | Yes | `InstaPay`, `POS`, `Mobile_Wallet`, `ATM`, `Web` | Transaction payment rail |
| `category` | `TransactionCategory` | Yes | Retail, Groceries, Utilities, Healthcare, etc. | Merchant category code classification |
| `amount_egp` | `Decimal` | Yes | > 0.00, <= 5,000,000.00, 2 decimals | Transaction volume in Egyptian Pounds (EGP) |
| `status` | `TransactionStatus` | Yes | `COMPLETED`, `DECLINED`, `REVERSED` | Execution status lifecycle state |
| `risk_score` | `float` | Yes | 0.0 <= score <= 100.0 | Automated fraud risk score assessment |

---

### 2.2 Macroeconomic Indicator Contract

- **Dataset Identifier**: `macroeconomic_indicators`
- **Domain**: `macroeconomics`
- **Schema Version**: `1.0.0`
- **Source Classification**: `real_public`
- **Implementation**: [`EconomicIndicatorContract`](file:///e:/Progects/efidp-platform/src/efidp/contracts/indicator.py)
- **JSON Schema Path**: `data/contracts/indicator.schema.json`

Captures macroeconomic time series (inflation, GDP growth, interest rates, foreign reserves) sourced from institutions such as the Central Bank of Egypt (CBE) and the World Bank.

#### Field Definitions & Constraints

| Field | Type | Required | Constraints | Semantic Description |
| :--- | :--- | :--- | :--- | :--- |
| `indicator_code` | `str` | Yes | Min length: 2, max length: 64, e.g., `EG.CPI.TOTL` | Canonical indicator code |
| `observation_date` | `date` | Yes | <= today | Observation period reference date |
| `value` | `float` | Yes | Finite float (no NaN / Inf) | Measured indicator numeric value |
| `previous_value` | `float` | No | Optional, finite float | Previous period observation value |
| `unit` | `str` | Yes | Min length: 1, max length: 32, e.g., `PERCENT`, `USD_BILLIONS` | Unit of measurement |
| `source` | `str` | Yes | Min length: 2, max length: 64, e.g., `World_Bank`, `CBE` | Institutional issuing source |
| `frequency` | `Frequency` | Yes | `ANNUAL`, `SEMI_ANNUAL`, `QUARTERLY`, `MONTHLY`, `DAILY` | Reporting periodicity |
| `metadata` | `dict[str, Any]`| No | Key-value pairs | Additional source annotations or revision notes |

---

### 2.3 Market Data Contract

- **Dataset Identifier**: `market_data`
- **Domain**: `capital_markets`
- **Schema Version**: `1.0.0`
- **Source Classification**: `real_public`
- **Implementation**: [`MarketDataContract`](file:///e:/Progects/efidp-platform/src/efidp/contracts/market.py)
- **JSON Schema Path**: `data/contracts/market.schema.json`

Captures daily and intra-day trading records for Egyptian Exchange (EGX) indices (e.g., EGX30, EGX70) and equities.

#### Field Definitions & Constraints

| Field | Type | Required | Constraints | Semantic Description |
| :--- | :--- | :--- | :--- | :--- |
| `asset_code` | `str` | Yes | Min length: 2, max length: 32, uppercase | Ticker or index symbol (e.g., `EGX30`) |
| `trading_date` | `date` | Yes | <= today | Calendar trading date |
| `open_price` | `Decimal` | No | >= 0.0001, 4 decimal places | Trading day opening price |
| `high_price` | `Decimal` | No | >= 0.0001, 4 decimal places, must be >= low, open, close | Trading day maximum session price |
| `low_price` | `Decimal` | No | >= 0.0001, 4 decimal places, must be <= high, open, close | Trading day minimum session price |
| `close_price` | `Decimal` | Yes | >= 0.0001, 4 decimal places | Session closing price |
| `volume` | `int` | No | >= 0 | Number of shares / contracts traded |
| `turnover_egp` | `Decimal` | No | >= 0.00, 2 decimal places | Total traded currency value in EGP |

*Cross-field validation*: Whenever `high_price` and `low_price` are provided, the contract validates that `high_price >= low_price`, `high_price >= open_price`, `high_price >= close_price`, `low_price <= open_price`, and `low_price <= close_price`.

---

### 2.4 Ingestion Metadata Envelope Contract

- **Dataset Identifier**: `ingestion_envelope_metadata`
- **Domain**: `data_engineering`
- **Schema Version**: `1.0.0`
- **Source Classification**: `derived`
- **Implementation**: [`IngestionEnvelope[T]`](file:///e:/Progects/efidp-platform/src/efidp/contracts/envelope.py)
- **JSON Schema Path**: `data/contracts/envelope.schema.json`

Wraps extracted batches to provide tamper-evident cryptographic provenance, extraction metrics, and schema alignment.

#### Metadata Envelope Header Fields

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `ingestion_id` | `UUID4` | Non-null | Unique pipeline execution run identifier |
| `source_id` | `str` | Validated against registry | Source identifier matching `config/sources.yaml` |
| `source_type` | `SourceClassification` | `real_public`, `synthetic`, `derived` | Classification of the payload origin |
| `dataset_name` | `str` | Matches registered contract name | Target dataset classification |
| `schema_version` | `str` | SemVer format (e.g. `1.0.0`) | Schema version expected for records |
| `extracted_at` | `datetime` | UTC ISO-8601 | Ingestion completion timestamp |
| `payload_hash` | `str` | SHA-256 (64 hex characters) | Cryptographic hash of the raw payload |
| `row_count` | `int` | >= 0, matches payload length | Record count inside payload |
| `extraction_start_time` | `datetime` | <= extraction_end_time | Extraction task initiation timestamp |
| `extraction_end_time` | `datetime` | >= extraction_start_time | Extraction task completion timestamp |

---

## 3. Schema Versioning & Evolution

EFIDP enforces strict semantic versioning: `MAJOR.MINOR.PATCH` (e.g., `1.0.0`).

### 3.1 Version Compatibility Rules

1. **PATCH (e.g., 1.0.0 -> 1.0.1)**:
   - Non-functional changes (documentation corrections, description updates, internal optimizations).
   - Zero modifications to field types, names, or constraint ranges.
   - Backward and forward compatible.
2. **MINOR (e.g., 1.0.0 -> 1.1.0)**:
   - Backward-compatible additions only.
   - Adding a new **optional** field with a default value.
   - Loosening an existing constraint (e.g., increasing upper transaction bound from 5M to 10M EGP).
   - Old consumers continue reading new records without failure.
3. **MAJOR (e.g., 1.0.0 -> 2.0.0)**:
   - Breaking modifications requiring consumer migration.
   - Adding a mandatory field without a default.
   - Renaming or deleting an existing field.
   - Changing a field type or tightening validation boundaries.
   - Producers must route major version changes through a new topic / endpoint or schema negotiation header.

### 3.2 Consumer Identification & Verification

Consumers inspect the `schema_version` attribute within the `IngestionMetadata` envelope. If the major version does not match the consumer's expected contract, the batch is rejected with [`SchemaVersionMismatchError`](file:///e:/Progects/efidp-platform/src/efidp/core/exceptions.py) before attempting deserialization.

---

## 4. Validation Framework & Error Model

The [`ContractValidator`](file:///e:/Progects/efidp-platform/src/efidp/contracts/validator.py) provides machine-readable, structured validation APIs:

```python
from efidp.contracts.validator import ContractValidator
from efidp.contracts.transaction import FinancialTransactionContract

# 1. Single Record Validation
result = ContractValidator.validate_record(FinancialTransactionContract, raw_dict)
if not result.is_valid:
    for err in result.errors:
        print(f"Field: {err.field}, Error: {err.error_type}, Message: {err.message}")

# 2. Batch Validation
batch_result = ContractValidator.validate_batch(
    FinancialTransactionContract, records_list, fail_fast=False
)
print(
    f"Pass Rate: {batch_result.pass_rate * 100}% ({batch_result.valid_records}/{batch_result.total_records})"
)

# 3. Envelope Validation
is_envelope_valid, envelope_result = ContractValidator.validate_envelope(
    raw_envelope_dict, expected_contract=FinancialTransactionContract
)
```

### Distinction Between Validation & System Errors

- **Contract Validation Errors** ([`ContractValidationError`](file:///e:/Progects/efidp-platform/src/efidp/core/exceptions.py)):
  Subclass of `DataQualityError`. Indicates bad, corrupt, or unformatted input payload. Never causes unhandled process crashes; results in dead-letter routing and structured logging.
- **System / Ingestion Errors** ([`SourceExtractionError`](file:///e:/Progects/efidp-platform/src/efidp/core/exceptions.py), [`ConfigurationError`](file:///e:/Progects/efidp-platform/src/efidp/core/exceptions.py)):
  Infrastructure, network timeout, or file system failures. Subject to retry policies before escalating.

---

## 5. Sample Payloads

Representative fixtures are cataloged in `data/sample/`:

| Fixture Path | Description | Valid? |
| :--- | :--- | :--- |
| [`data/sample/valid_transaction.json`](file:///e:/Progects/efidp-platform/data/sample/valid_transaction.json) | Standard retail POS transaction in Cairo | Yes |
| [`data/sample/invalid_transaction.json`](file:///e:/Progects/efidp-platform/data/sample/invalid_transaction.json) | Violates EGP limit, risk score range, unknown governorate | No |
| [`data/sample/valid_economic_indicator.json`](file:///e:/Progects/efidp-platform/data/sample/valid_economic_indicator.json) | Egypt Headline Inflation rate from CBE | Yes |
| [`data/sample/invalid_economic_indicator.json`](file:///e:/Progects/efidp-platform/data/sample/invalid_economic_indicator.json) | Observation date set in future, missing source | No |
| [`data/sample/valid_market_record.json`](file:///e:/Progects/efidp-platform/data/sample/valid_market_record.json) | EGX30 index daily closing session | Yes |
| [`data/sample/invalid_market_record.json`](file:///e:/Progects/efidp-platform/data/sample/invalid_market_record.json) | Inverted high/low bounds, negative volume | No |
| [`data/sample/valid_envelope.json`](file:///e:/Progects/efidp-platform/data/sample/valid_envelope.json) | Fully wrapped metadata envelope with valid payload hash | Yes |

---

## 6. Phase 4 Ingestion Consumption Pattern

In Phase 4, data ingestion pipelines (Airflow tasks, streaming workers, file consumers) will consume these contracts as follows:

```
[Raw Ingestion Source]
          |
          v
[Connector: APIDataSource / FileDataSource]
          |
          v
[ContractValidator.validate_batch()]
     /                         \
 (All Valid)               (Any Failure)
     |                             |
     v                             v
[Wrap IngestionEnvelope]    [Quarantine / Dead Letter Queue]
     |                             |
     v                             v
[Write to MinIO Bronze]     [Emit Prometheus Metric & Alert]
```
