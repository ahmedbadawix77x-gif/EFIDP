"""Formal Data Contract package for Egypt Financial Intelligence Data Platform (EFIDP)."""

from efidp.contracts.base import BaseDataContract, ContractMetadata
from efidp.contracts.enums import (
    ChannelType,
    ConnectorType,
    Frequency,
    Governorate,
    SourceClassification,
    TransactionCategory,
    TransactionStatus,
)
from efidp.contracts.envelope import (
    IngestionEnvelope,
    IngestionMetadata,
    compute_payload_hash,
)
from efidp.contracts.indicator import EconomicIndicatorRecord
from efidp.contracts.market import MarketObservationRecord
from efidp.contracts.schema import export_contract_schemas
from efidp.contracts.transaction import FinancialTransactionEvent
from efidp.contracts.validator import (
    BatchValidationResult,
    ContractValidator,
    ValidationErrorDetail,
    ValidationResult,
)

__all__ = [
    "BaseDataContract",
    "BatchValidationResult",
    "ChannelType",
    "ConnectorType",
    "ContractMetadata",
    "ContractValidator",
    "EconomicIndicatorRecord",
    "FinancialTransactionEvent",
    "Frequency",
    "Governorate",
    "IngestionEnvelope",
    "IngestionMetadata",
    "MarketObservationRecord",
    "SourceClassification",
    "TransactionCategory",
    "TransactionStatus",
    "ValidationErrorDetail",
    "ValidationResult",
    "compute_payload_hash",
    "export_contract_schemas",
]
