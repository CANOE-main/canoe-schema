#!/usr/bin/env python3
"""
migrate.py — Migrate a CANOE SQLite database from schema v3.1 to v3.2.

Usage:
    python migrate.py <sqlite_db> [--duplicate-tech {error,warn,fix}] [--dry-run]

Phases:
    1. Preflight  — verify the database is a valid v3.1 schema.
    2. Label pop  — populate TechnologyLabel, CommodityLabel, DataSourceLabel.
    3. Dup check  — detect technologies with the same name across datasets.
    4. LACF       — migrate LimitAnnualCapacityFactor (period → vintage).
    5. TimePeriod — upsert canonical 3.2 time periods.
    6. Version    — update DB_MAJOR / DB_MINOR in MetaData.

The entire migration runs inside a single transaction. Any error triggers a
full rollback so the source database is never left in a partial state.
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
from enum import Enum
from pathlib import Path

from loguru import logger

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EXPECTED_SOURCE_VERSION = (3, 1)
MIGRATION_SQL = Path(__file__).parent / "migrate.sql"

# Path to match_schema.py relative to this file:
#   schema/v3_1/migrations/to_v3_2/migrate.py
#   tools/match_schema.py
_REPO_ROOT = Path(__file__).resolve().parents[4]
_MATCH_SCHEMA = _REPO_ROOT / "tools" / "match_schema.py"


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class DuplicateTechPolicy(str, Enum):
    ERROR = "error"   # Abort the migration (default)
    WARN  = "warn"    # Log a warning and continue; duplicates left as-is
    FIX   = "fix"     # Keep the entry with the most Efficiency references
                      # (tiebreak: alphabetically lowest data_id)


# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------

def _preflight(db_path: Path) -> None:
    """
    Verify the database looks like a v3.1 schema before touching anything.

    Uses match_schema.parse_sql_signature / classify if available; falls back
    to a lightweight MetaData version check so the tool works even when the
    repo layout isn't fully set up.
    """
    logger.info("Preflight: checking source schema version …")

    # Fast path: try the match_schema tool for a structural check.
    if _MATCH_SCHEMA.exists():
        sys.path.insert(0, str(_MATCH_SCHEMA.parent))
        try:
            from match_schema import classify, parse_sql_signature  # type: ignore

            schema_31_sql = _REPO_ROOT / "schema" / "v3_1" / "schema_3_1.sql"
            if schema_31_sql.exists():
                sigs = [parse_sql_signature(schema_31_sql, "3.1")]
                result = classify(db_path, sigs)
                best = result.get("best_match")
                if best and best["score"] < 0.8:
                    raise SystemExit(
                        f"Preflight failed: database does not look like a v3.1 schema "
                        f"(best match score {best['score']:.2f}). Aborting."
                    )
                logger.debug(
                    f"Structural match score against v3.1: {best['score'] if best else 'n/a'}"
                )
        except ImportError:
            logger.warning("match_schema module found but could not be imported; "
                           "falling back to MetaData version check.")
        finally:
            sys.path.pop(0)

    # Always verify the MetaData version regardless.
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        row = cur.execute(
            "SELECT element, value FROM MetaData "
            "WHERE element IN ('DB_MAJOR', 'DB_MINOR')"
        ).fetchall()
        meta = {r[0]: int(r[1]) for r in row}
        major = meta.get("DB_MAJOR")
        minor = meta.get("DB_MINOR")
        if (major, minor) != EXPECTED_SOURCE_VERSION:
            raise SystemExit(
                f"Preflight failed: expected MetaData version "
                f"{EXPECTED_SOURCE_VERSION[0]}.{EXPECTED_SOURCE_VERSION[1]}, "
                f"got {major}.{minor}. Aborting."
            )
        logger.success(f"Preflight passed: database reports version {major}.{minor}.")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Phase 2 — Duplicate technology detection & resolution
# ---------------------------------------------------------------------------

def _find_duplicate_techs(cur: sqlite3.Cursor) -> dict[str, list[str]]:
    """
    Return a mapping of {tech_name: [data_id, ...]} for any tech name that
    appears in more than one dataset.
    """
    rows = cur.execute(
        """
        SELECT tech, GROUP_CONCAT(data_id, '|') AS ids, COUNT(*) AS cnt
        FROM Technology
        GROUP BY tech
        HAVING cnt > 1
        """
    ).fetchall()
    return {tech: sorted(ids.split("|")) for tech, ids, _ in rows}


def _count_efficiency_refs(cur: sqlite3.Cursor, tech: str, data_id: str) -> int:
    """Count Efficiency rows that reference a given (tech, data_id) pair."""
    row = cur.execute(
        "SELECT COUNT(*) FROM Efficiency WHERE tech = ? AND data_id = ?",
        (tech, data_id),
    ).fetchone()
    return row[0] if row else 0


def _resolve_duplicates(
    cur: sqlite3.Cursor,
    duplicates: dict[str, list[str]],
    policy: DuplicateTechPolicy,
) -> None:
    """
    Handle duplicate tech names according to the chosen policy.

    FIX strategy:
      - Count Efficiency references per (tech, data_id).
      - Keep the data_id with the most references.
      - Tiebreak: alphabetically lowest data_id.
      - Delete Technology rows for losing data_ids.
        (Data in child tables referencing the losing data_id is left intact;
         the label tables introduced in 3.2 decouple the global name from the
         dataset-scoped config, so orphaned dataset rows are acceptable.)
    """
    if not duplicates:
        return

    tech_list = ", ".join(f"'{t}'" for t in duplicates)

    if policy == DuplicateTechPolicy.ERROR:
        summary = "; ".join(
            f"'{tech}' in datasets [{', '.join(ids)}]"
            for tech, ids in duplicates.items()
        )
        raise SystemExit(
            f"Migration aborted: duplicate technology names found across datasets — "
            f"{summary}.\n"
            f"Re-run with --duplicate-tech warn or --duplicate-tech fix to continue."
        )

    if policy == DuplicateTechPolicy.WARN:
        for tech, ids in duplicates.items():
            logger.warning(
                f"Duplicate tech '{tech}' exists in datasets: {ids}. "
                f"Proceeding without changes (--duplicate-tech warn)."
            )
        return

    # policy == FIX
    for tech, data_ids in duplicates.items():
        scored: list[tuple[int, str]] = []
        for data_id in data_ids:
            refs = _count_efficiency_refs(cur, tech, data_id)
            scored.append((refs, data_id))

        # Sort: most refs first; tiebreak alphabetically on data_id (lowest wins).
        scored.sort(key=lambda x: (-x[0], x[1]))
        winner_refs, winner_id = scored[0]
        losers = [data_id for _, data_id in scored[1:]]

        logger.info(
            f"Tech '{tech}': keeping data_id='{winner_id}' "
            f"({winner_refs} Efficiency refs). "
            f"Removing: {losers}."
        )
        for loser_id in losers:
            cur.execute(
                "DELETE FROM Technology WHERE tech = ? AND data_id = ?",
                (tech, loser_id),
            )


# ---------------------------------------------------------------------------
# Phase 3 — LimitAnnualCapacityFactor warning
# ---------------------------------------------------------------------------

def _warn_lacf(cur: sqlite3.Cursor) -> None:
    """
    Warn the user that LimitAnnualCapacityFactor will be structurally changed:
    the `period` column will be renamed to `vintage`. Existing period values
    are carried over as-is (best-effort default).
    """
    count = cur.execute("SELECT COUNT(*) FROM LimitAnnualCapacityFactor").fetchone()[0]
    if count == 0:
        logger.info(
            "LimitAnnualCapacityFactor is empty — period→vintage migration is a no-op."
        )
    else:
        logger.warning(
            f"LimitAnnualCapacityFactor contains {count} row(s). "
            f"The `period` column will be renamed to `vintage` and existing period "
            f"values will be carried over unchanged. Review these rows after migration "
            f"to confirm the vintage values are correct."
        )


# ---------------------------------------------------------------------------
# Core migration runner
# ---------------------------------------------------------------------------

def _run_migration_sql(conn: sqlite3.Connection) -> None:
    """Execute the SQL migration script against an open connection."""
    sql = MIGRATION_SQL.read_text(encoding="utf-8")
    # Split on semicolons but skip empty statements (comments, blank lines).
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    cur = conn.cursor()
    for stmt in statements:
        cur.execute(stmt)


def migrate(
    db_path: Path,
    policy: DuplicateTechPolicy,
    dry_run: bool,
) -> None:
    # ── Preflight ────────────────────────────────────────────────────────────
    _preflight(db_path)

    # ── Backup ───────────────────────────────────────────────────────────────
    backup_path = db_path.with_suffix(".v3_1.bak")
    logger.info(f"Creating backup: {backup_path}")
    shutil.copy2(db_path, backup_path)

    # ── Open connection (single transaction) ─────────────────────────────────
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = OFF")  # Required for table restructuring
    conn.execute("BEGIN")

    try:
        cur = conn.cursor()

        # ── Phase 2: Duplicate tech detection ────────────────────────────────
        logger.info("Phase 2: Checking for duplicate technology names …")
        duplicates = _find_duplicate_techs(cur)
        if duplicates:
            logger.info(
                f"Found {len(duplicates)} tech name(s) appearing in multiple datasets."
            )
        else:
            logger.info("No duplicate technology names found.")
        _resolve_duplicates(cur, duplicates, policy)

        # ── Phase 3: LACF warning ─────────────────────────────────────────────
        logger.info("Phase 3: LimitAnnualCapacityFactor structural change …")
        _warn_lacf(cur)

        # ── Run SQL (phases 1, 3, 4, 5) ───────────────────────────────────────
        if dry_run:
            logger.warning("Dry run enabled — SQL migration will NOT be applied.")
        else:
            logger.info("Applying SQL migration …")
            _run_migration_sql(conn)
            conn.execute("PRAGMA foreign_keys = ON")
            conn.commit()
            logger.success("Migration committed successfully.")

    except Exception as exc:
        conn.rollback()
        logger.error(f"Migration failed — rolling back. Reason: {exc}")
        logger.info(f"Your original database is untouched. Backup is at: {backup_path}")
        conn.close()
        raise SystemExit(1) from exc

    conn.close()

    if not dry_run:
        logger.success(
            f"Database '{db_path}' has been migrated to schema v3.2.\n"
            f"Backup of the original v3.1 database: {backup_path}"
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _configure_logging(verbose: bool) -> None:
    logger.remove()
    level = "DEBUG" if verbose else "INFO"
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | {message}",
        colorize=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrate a CANOE SQLite database from schema v3.1 to v3.2.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "sqlite_db",
        type=Path,
        help="Path to the SQLite database file to migrate.",
    )
    parser.add_argument(
        "--duplicate-tech",
        choices=[p.value for p in DuplicateTechPolicy],
        default=DuplicateTechPolicy.ERROR.value,
        dest="duplicate_tech",
        help=(
            "How to handle technology names that appear in multiple datasets. "
            "'error' (default): abort the migration. "
            "'warn': log a warning and continue without changes. "
            "'fix': keep the entry with the most Efficiency references "
            "(tiebreak: alphabetically lowest data_id)."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run all checks and print what would happen, but do not modify the database.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug-level logging.",
    )

    args = parser.parse_args()
    _configure_logging(args.verbose)

    db_path = args.sqlite_db.resolve()
    if not db_path.exists():
        logger.error(f"Database file not found: {db_path}")
        raise SystemExit(1)

    policy = DuplicateTechPolicy(args.duplicate_tech)
    migrate(db_path, policy, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
