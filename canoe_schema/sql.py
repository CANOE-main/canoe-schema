"""Access bundled SQL schema files for each CANOE schema version.

SQL files are colocated with their respective version packages
(e.g. ``canoe_schema/v3_1/schema.sql``) and shipped as package data.
Use :func:`get_sql_schema` when you only need the SQL text, and
:func:`get_sql_schema_path` when a downstream tool requires a real
filesystem path (e.g. the ``sqlite3`` CLI or ``match_schema.py``).
"""

from __future__ import annotations

from contextlib import contextmanager
from importlib import resources
from importlib.abc import Traversable
from pathlib import Path
from typing import Generator


def _schema_ref(version: str) -> Traversable:
    """Return an :class:`importlib.resources.Traversable` for a schema file.

    The traversable is an abstract handle that works across all install types
    (regular wheel, editable install, zipimport). It should not be used as a
    filesystem path directly — use :func:`get_sql_schema` or
    :func:`get_sql_schema_path` instead.

    Args:
        version: Version string in dot or underscore form (e.g. ``"3.1"``
            or ``"3_1"``).

    Returns:
        A :class:`~importlib.abc.Traversable` pointing to ``schema.sql``
        inside the corresponding version sub-package.

    Raises:
        ModuleNotFoundError: If the version sub-package (e.g.
            ``canoe_schema.v3_1``) does not exist in the installed package.
    """
    v = version.replace(".", "_")
    package = f"canoe_schema.v{v}"
    try:
        return resources.files(package).joinpath("schema.sql")
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            f"Schema version '{version}' not found. "
            f"Expected package '{package}' to exist inside canoe_schema."
        ) from exc


def get_sql_schema(version: str) -> str:
    """Load the SQL schema for a specific CANOE version as a string.

    This is the preferred way to access schema content at runtime. The file
    is read through :mod:`importlib.resources` and works regardless of how
    the package was installed.

    Args:
        version: Version string in dot or underscore form (e.g. ``"3.1"``
            or ``"3_1"``).

    Returns:
        The full SQL schema as a UTF-8 string.

    Raises:
        ModuleNotFoundError: If no sub-package exists for the given version.
        FileNotFoundError: If the sub-package exists but ``schema.sql`` is
            missing (indicates a broken installation).

    Example::

        sql = get_sql_schema("3.1")
        conn.executescript(sql)
    """
    ref = _schema_ref(version)
    try:
        return ref.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"schema.sql not found for version '{version}'. "
            f"The package may be installed incorrectly."
        ) from exc


@contextmanager
def schema_path(version: str) -> Generator[Path, None, None]:
    """Context manager that yields a real filesystem path to a schema file.

    Most code should prefer :func:`get_sql_schema` for reading content.
    Use this only when a downstream tool requires an actual path on disk
    (e.g. ``match_schema.py``, the ``sqlite3`` CLI, or test fixtures that
    call ``sqlite3.connect()`` with a file URI).

    The path is only guaranteed to exist for the duration of the ``with``
    block. Outside the block the underlying temporary file (if any) may be
    cleaned up by :func:`importlib.resources.as_file`.

    Args:
        version: Version string in dot or underscore form (e.g. ``"3.1"``
            or ``"3_1"``).

    Yields:
        A :class:`~pathlib.Path` pointing to ``schema.sql`` on disk.

    Raises:
        ModuleNotFoundError: If no sub-package exists for the given version.
        FileNotFoundError: If the sub-package exists but ``schema.sql`` is
            missing (indicates a broken installation).

    Example::

        with schema_path("3.2") as path:
            subprocess.run(["sqlite3", str(db), f".read {path}"])
    """
    ref = _schema_ref(version)
    with resources.as_file(ref) as path:
        yield path