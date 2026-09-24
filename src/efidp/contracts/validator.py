"""Machine-readable contract validation utilities for single records, batches, and envelopes."""

from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from efidp.contracts.base import BaseDataContract
from efidp.contracts.envelope import IngestionEnvelope, IngestionMetadata

T = TypeVar("T", bound=BaseDataContract)


class ValidationErrorDetail(BaseModel):
    """Structured, machine-readable validation failure detail."""

    field: str = Field(..., description="Target property or field path that failed validation")
    error_type: str = Field(..., description="Classification category of the validation failure")
    message: str = Field(..., description="Human-readable explanation of why the rule failed")
    input_value: Any | None = Field(
        default=None, description="Raw input value that caused the failure"
    )

    model_config = ConfigDict(extra="ignore")


class ValidationResult(BaseModel):
    """Validation outcome for an individual record or entity."""

    is_valid: bool = Field(..., description="True if record passed all contract validations")
    dataset_name: str = Field(..., description="Dataset name associated with the contract")
    schema_version: str = Field(
        ..., description="Schema version against which the record was validated"
    )
    record_id: str | None = Field(
        default=None, description="Identifier of the record if discernible"
    )
    errors: list[ValidationErrorDetail] = Field(
        default_factory=list, description="List of discrete field-level validation errors"
    )
    validated_data: dict[str, Any] | None = Field(
        default=None, description="Cleaned, coerced data dictionary if valid"
    )

    model_config = ConfigDict(extra="ignore")


class BatchValidationResult(BaseModel):
    """Aggregated validation statistics and outcomes for an ingestion batch."""

    total_records: int = Field(..., ge=0, description="Total records evaluated in the batch")
    valid_records: int = Field(..., ge=0, description="Count of successfully validated records")
    invalid_records: int = Field(..., ge=0, description="Count of rejected invalid records")
    pass_rate: float = Field(..., ge=0.0, le=1.0, description="Pass percentage ratio (0.0 to 1.0)")
    is_valid: bool = Field(..., description="True if 100% of records passed validation")
    results: list[ValidationResult] = Field(
        default_factory=list, description="Individual record validation results"
    )
    errors_summary: dict[str, int] = Field(
        default_factory=dict, description="Summary counts of error types encountered across batch"
    )

    model_config = ConfigDict(extra="ignore")


class ContractValidator:
    """Enterprise contract validation service for EFIDP payloads."""

    @classmethod
    def validate_record(
        cls,
        contract_cls: type[T],
        data: dict[str, Any],
        record_id_field: str | None = None,
    ) -> ValidationResult:
        """Validate a single dictionary payload against an EFIDP data contract."""
        meta = contract_cls.get_contract_metadata()
        rec_id: str | None = None

        if record_id_field and record_id_field in data:
            rec_id = str(data[record_id_field])
        elif "transaction_id" in data:
            rec_id = str(data["transaction_id"])
        elif "indicator_code" in data:
            rec_id = str(data["indicator_code"])
        elif "asset_code" in data:
            rec_id = str(data["asset_code"])

        try:
            instance = contract_cls.model_validate(data)
            return ValidationResult(
                is_valid=True,
                dataset_name=meta.dataset_name,
                schema_version=meta.schema_version,
                record_id=rec_id,
                errors=[],
                validated_data=instance.model_dump(mode="json"),
            )
        except ValidationError as e:
            errors: list[ValidationErrorDetail] = []
            for err in e.errors():
                loc = ".".join(str(p) for p in err.get("loc", []))
                input_val = err.get("input")
                errors.append(
                    ValidationErrorDetail(
                        field=loc or "root",
                        error_type=err.get("type", "value_error"),
                        message=err.get("msg", "Validation failed"),
                        input_value=input_val,
                    )
                )

            return ValidationResult(
                is_valid=False,
                dataset_name=meta.dataset_name,
                schema_version=meta.schema_version,
                record_id=rec_id,
                errors=errors,
                validated_data=None,
            )

    @classmethod
    def validate_batch(
        cls,
        contract_cls: type[T],
        records: list[dict[str, Any]],
        record_id_field: str | None = None,
    ) -> BatchValidationResult:
        """Validate a sequence of dictionary payloads against an EFIDP data contract."""
        total = len(records)
        if total == 0:
            return BatchValidationResult(
                total_records=0,
                valid_records=0,
                invalid_records=0,
                pass_rate=1.0,
                is_valid=True,
                results=[],
                errors_summary={},
            )

        results: list[ValidationResult] = []
        valid_count = 0
        error_summary: dict[str, int] = {}

        for rec in records:
            res = cls.validate_record(contract_cls, rec, record_id_field=record_id_field)
            results.append(res)
            if res.is_valid:
                valid_count += 1
            else:
                for err in res.errors:
                    error_summary[err.error_type] = error_summary.get(err.error_type, 0) + 1

        invalid_count = total - valid_count
        pass_rate = round(valid_count / total, 4)

        return BatchValidationResult(
            total_records=total,
            valid_records=valid_count,
            invalid_records=invalid_count,
            pass_rate=pass_rate,
            is_valid=(invalid_count == 0),
            results=results,
            errors_summary=error_summary,
        )

    @classmethod
    def validate_envelope(
        cls,
        envelope_data: dict[str, Any],
        payload_contract_cls: type[T] | None = None,
    ) -> ValidationResult:
        """Validate an IngestionEnvelope and optionally validate its nested payload."""
        meta_dict = envelope_data.get("metadata", {})
        payload = envelope_data.get("payload")

        # 1. Validate envelope metadata
        try:
            IngestionMetadata.model_validate(meta_dict)
        except ValidationError as e:
            errors = [
                ValidationErrorDetail(
                    field=f"metadata.{'.'.join(str(p) for p in err.get('loc', []))}",
                    error_type=err.get("type", "value_error"),
                    message=err.get("msg", "Invalid metadata field"),
                    input_value=err.get("input"),
                )
                for err in e.errors()
            ]
            return ValidationResult(
                is_valid=False,
                dataset_name=str(meta_dict.get("dataset_name", "unknown")),
                schema_version=str(meta_dict.get("schema_version", "unknown")),
                record_id=str(meta_dict.get("ingestion_id")),
                errors=errors,
            )

        # 2. Optionally validate payload against specified contract
        if payload_contract_cls is not None:
            if isinstance(payload, list):
                batch_res = cls.validate_batch(payload_contract_cls, payload)
                if not batch_res.is_valid:
                    flat_errors: list[ValidationErrorDetail] = []
                    for idx, r in enumerate(batch_res.results):
                        for err in r.errors:
                            flat_errors.append(
                                ValidationErrorDetail(
                                    field=f"payload[{idx}].{err.field}",
                                    error_type=err.error_type,
                                    message=err.message,
                                    input_value=err.input_value,
                                )
                            )
                    return ValidationResult(
                        is_valid=False,
                        dataset_name=str(meta_dict.get("dataset_name")),
                        schema_version=str(meta_dict.get("schema_version")),
                        record_id=str(meta_dict.get("ingestion_id")),
                        errors=flat_errors,
                    )
            elif isinstance(payload, dict):
                single_res = cls.validate_record(payload_contract_cls, payload)
                if not single_res.is_valid:
                    envelope_errors = [
                        ValidationErrorDetail(
                            field=f"payload.{err.field}",
                            error_type=err.error_type,
                            message=err.message,
                            input_value=err.input_value,
                        )
                        for err in single_res.errors
                    ]
                    return ValidationResult(
                        is_valid=False,
                        dataset_name=str(meta_dict.get("dataset_name")),
                        schema_version=str(meta_dict.get("schema_version")),
                        record_id=str(meta_dict.get("ingestion_id")),
                        errors=envelope_errors,
                    )
            else:
                return ValidationResult(
                    is_valid=False,
                    dataset_name=str(meta_dict.get("dataset_name")),
                    schema_version=str(meta_dict.get("schema_version")),
                    record_id=str(meta_dict.get("ingestion_id")),
                    errors=[
                        ValidationErrorDetail(
                            field="payload",
                            error_type="type_error",
                            message=f"Payload must be a list or dict, got {type(payload).__name__}",
                            input_value=payload,
                        )
                    ],
                )

        # 3. Everything valid
        envelope_inst = IngestionEnvelope[Any].model_validate(envelope_data)
        return ValidationResult(
            is_valid=True,
            dataset_name=str(meta_dict.get("dataset_name")),
            schema_version=str(meta_dict.get("schema_version")),
            record_id=str(meta_dict.get("ingestion_id")),
            errors=[],
            validated_data=envelope_inst.model_dump(mode="json"),
        )
