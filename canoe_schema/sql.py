"""Access SQL schema files for different CANOE schema versions."""
from __future__ import annotations

from importlib import resources
from pathlib import Path


def _schema_root() -> Path:
    """Return the root of the schema/ directory, regardless of install type."""
    # Anchor to the canoe_schema package, then step into the bundled schema/ dir.
    # This works for regular installs, editable installs, and zipimport.
    ref = resources.files("canoe_schema")
    # schema/ is shipped as an artifact alongside the package; resolve via the
    # package anchor so importlib handles the path abstraction correctly.
    return Path(str(ref)).parent / "schema"


def get_sql_schema(version: str) -> str:
    """Load SQL schema for a specific version.

    Args:
        version: Version string in dot or underscore form (e.g. "3.1" or "3_1")

    Returns:
        The SQL schema as a string

    Raises:
        FileNotFoundError: If the schema version doesn't exist
    """
    v = version.replace(".", "_")
    schema_file = _schema_root() / f"v{v}" / f"schema_{v}.sql"
    if not schema_file.exists():
        raise FileNotFoundError(
            f"Schema v{version} not found. Expected file: {schema_file}"
        )
    return schema_file.read_text(encoding="utf-8")


def get_sql_schema_path(version: str) -> Path:
    """Get the filesystem path to a schema file.

    Note: prefer get_sql_schema() for reading content — this path is only
    valid for tools that explicitly need a filesystem path (e.g. sqlite3 CLI).
    """
    v = version.replace(".", "_")
    return _schema_root() / f"v{v}" / f"schema_{v}.sql"