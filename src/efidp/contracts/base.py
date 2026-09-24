"""Base data contract abstractions and metadata definitions."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from efidp.contracts.enums import SourceClassification


class ContractMetadata(BaseModel):
    """Formal metadata definition describing an EFIDP data contract."""

    dataset_name: str = Field(..., description="Canonical dataset identifier")
    domain: str = Field(..., description="Business or analytical domain")
    schema_version: str = Field(..., description="Semantic version of the schema (e.g., 1.0.0)")
    source_classification: SourceClassification = Field(
        ..., description="Data origin classification (real_public, synthetic, derived)"
    )
    description: str = Field(..., description="Semantic description of the contract purpose")

    model_config = ConfigDict(frozen=True)


class BaseDataContract(BaseModel):
    """Base class for all strongly-typed EFIDP data contracts.

    Enforces strict validation, forbidden extra fields, whitespace stripping,
    and programmatic access to JSON Schema and metadata.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    @classmethod
    def get_contract_metadata(cls) -> ContractMetadata:
        """Return the formal metadata definition for this contract."""
        raise NotImplementedError("Subclasses must implement get_contract_metadata()")

    @classmethod
    def get_json_schema(cls) -> dict[str, Any]:
        """Export the formal JSON Schema draft representation for this contract."""
        schema = cls.model_json_schema()
        meta = cls.get_contract_metadata()
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        schema["title"] = meta.dataset_name
        schema["description"] = meta.description
        schema["x-domain"] = meta.domain
        schema["x-schema-version"] = meta.schema_version
        schema["x-source-classification"] = meta.source_classification.value
        return schema
