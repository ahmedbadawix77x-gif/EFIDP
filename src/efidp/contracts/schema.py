"""JSON Schema generator and registry exporter for EFIDP data contracts."""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from efidp.contracts.envelope import IngestionEnvelope, IngestionMetadata
from efidp.contracts.indicator import EconomicIndicatorRecord
from efidp.contracts.market import MarketObservationRecord
from efidp.contracts.transaction import FinancialTransactionEvent

CONTRACT_REGISTRY: dict[str, type[BaseModel]] = {
    "transaction.schema.json": FinancialTransactionEvent,
    "indicator.schema.json": EconomicIndicatorRecord,
    "market.schema.json": MarketObservationRecord,
    "envelope_metadata.schema.json": IngestionMetadata,
    "envelope.schema.json": IngestionEnvelope[dict[str, Any]],
}


def export_contract_schemas(output_dir: Path | str | None = None) -> list[Path]:
    """Export standard JSON Schema draft representations to the specified directory.

    If output_dir is None, exports to data/contracts/ relative to project root.
    """
    if output_dir is None:
        target_dir = Path(__file__).resolve().parents[3] / "data" / "contracts"
    else:
        target_dir = Path(output_dir)

    target_dir.mkdir(parents=True, exist_ok=True)
    exported_files: list[Path] = []

    for filename, model_cls in CONTRACT_REGISTRY.items():
        filepath = target_dir / filename
        schema = model_cls.model_json_schema()
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
            f.write("\n")
        exported_files.append(filepath)

    return exported_files


if __name__ == "__main__":  # pragma: no cover
    files = export_contract_schemas()
    for fp in files:
        print(f"Exported: {fp}")
