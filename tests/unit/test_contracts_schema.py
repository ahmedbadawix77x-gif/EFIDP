"""Unit tests for contract schema export utility."""

from pathlib import Path

from efidp.contracts.schema import export_contract_schemas


def test_export_contract_schemas(tmp_path: Path) -> None:
    # Test with custom output_dir
    exported = export_contract_schemas(output_dir=tmp_path)
    assert len(exported) == 5
    filenames = {p.name for p in exported}
    assert "transaction.schema.json" in filenames
    assert "indicator.schema.json" in filenames
    assert "market.schema.json" in filenames
    assert "envelope_metadata.schema.json" in filenames
    assert "envelope.schema.json" in filenames

    # Verify files are non-empty and readable JSON
    for path in exported:
        assert path.exists()
        assert path.stat().st_size > 50

    # Test with default output_dir
    default_exported = export_contract_schemas()
    assert len(default_exported) == 5
