"""Access SQL schema files for different CANOE schema versions."""

from __future__ import annotations

from importlib import resources
from pathlib import Path


def get_sql_schema(version: str) -> str:
    """Load SQL schema for a specific version.
    
    Args:
        version: Version string (e.g., "3_1", "3_2")
        
    Returns:
        The SQL schema as a string
        
    Raises:
        FileNotFoundError: If the schema version doesn't exist
    """
    try:
        # For Python 3.9+
        schema_dir = resources.files("canoe_schema").parent / "schema" / f"v{version}"
        schema_file = schema_dir / f"schema_{version}.sql"
        return schema_file.read_text(encoding="utf-8")
    except (AttributeError, FileNotFoundError) as e:
        raise FileNotFoundError(f"Schema v{version} not found") from e


def get_sql_schema_path(version: str) -> Path:
    """Get the filesystem path to a schema file."""
    import canoe_schema
    base_path = Path(canoe_schema.__file__).parent.parent
    return base_path / "schema" / f"v{version.replace('.', '_')}" / f"schema_{version.replace('.', '_')}.sql"