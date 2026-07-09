#!/usr/bin/env python3
"""
migrate.py — Migrate a CANOE SQLite database from schema v3.2 to v4.0.

Usage:
    python migrate.py <sqlite_db> [--output PATH] [--force]
                       [--collapse-policy {error,keep-earliest,keep-latest,average}]
                       [--discount-rate {keep,adopt-v4-default}]
                       [--tech-group-collision {warn,error}]
                       [--days-per-period N]
                       [--dry-run] [-v]

Unlike the v3.1 -> v3.2 migration, this one does NOT modify the source file
in place. Virtually every table is renamed from CamelCase to snake_case in
v4.0, and SQLite table names are case-insensitive -- `CREATE TABLE technology`
fails with "table already exists" while `Technology` is still present in the
same file. So this script instead:

  1. Creates a brand-new SQLite file and initializes it with the full v4.0
     schema (by executing canoe_schema/v4_0/schema.sql verbatim, so the
     target schema can never drift from the single source of truth).
  2. ATTACHes the source v3.2 database read-only under the alias `src`.
  3. Copies every table across, applying the exact column mapping the two
     schemas require (see migrate.sql for the ~68 tables that are a pure
     rename/addition, and the functions below for the ~10 tables that need
     a policy decision).
  4. Runs `PRAGMA foreign_key_check` on the result before declaring success.

The source database is never written to. There is no `.bak` file because
there is nothing to roll back -- if anything goes wrong, delete the
(incomplete) output file and re-run.

Phases:
    1. Preflight     — verify the source is a valid v3.2 schema.
    2. Schema create — build the v4.0 schema in the new output file.
    3. Static copy   — run migrate.sql (pure renames / additions, no policy).
    4. Collapse      — capacity_factor_process/tech, limit_seasonal_capacity_factor,
                        limit_storage_level_fraction, reserve_capacity_derate
                        (all drop `period` from the primary key).
    5. Time tables   — time_of_day.hours (no source equivalent), and
                        time_season / time_season_sequential .segment_fraction,
                        computed from the now-dropped TimeSegmentFraction /
                        num_days + days_per_period.
    6. Metadata      — economic rate policy (discount/loan rate) and version.
    7. Validation    — tech/tech_group namespace collision check, FK check.
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from loguru import logger

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EXPECTED_SOURCE_VERSION = (3, 2)
MIGRATION_SQL = Path(__file__).parent / "migrate.sql"

# Path layout: canoe_schema/v3_2/migrations/to_v4_0/migrate.py
_CANOE_SCHEMA_DIR = Path(__file__).resolve().parents[3]
_REPO_ROOT = Path(__file__).resolve().parents[4]
_MATCH_SCHEMA = _REPO_ROOT / "tools" / "match_schema.py"
V4_0_SCHEMA_SQL = _CANOE_SCHEMA_DIR / "v4_0" / "schema.sql"
V3_2_SCHEMA_SQL = _CANOE_SCHEMA_DIR / "v3_2" / "schema.sql"

DEFAULT_DAYS_PER_PERIOD = 365


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class CollapsePolicy(str, Enum):
    ERROR = "error"                # Abort if a genuine conflict is found (default)
    KEEP_EARLIEST = "keep-earliest"  # Keep the earliest period's row/value
    KEEP_LATEST = "keep-latest"      # Keep the latest period's row/value
    AVERAGE = "average"              # Average the numeric measure across periods


class DiscountRatePolicy(str, Enum):
    KEEP = "keep"                        # Preserve the source DB's existing rate (default)
    ADOPT_V4_DEFAULT = "adopt-v4-default"  # Overwrite with v4.0's new 0.05 default


class TechGroupCollisionPolicy(str, Enum):
    WARN = "warn"    # Log a loud warning and continue (default)
    ERROR = "error"  # Abort the migration


def _changes(cur: sqlite3.Cursor) -> int:
    """
    Row count of the last DML statement. cur.rowcount is unreliable (-1) for
    INSERT ... SELECT statements built on a WITH clause, so we ask SQLite's
    own change counter instead.
    """
    return cur.execute("SELECT changes()").fetchone()[0]


# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------

def _preflight(db_path: Path) -> None:
    """Verify the database looks like a v3.2 schema before touching anything."""
    logger.info("Preflight: checking source schema version …")

    if _MATCH_SCHEMA.exists() and V3_2_SCHEMA_SQL.exists():
        sys.path.insert(0, str(_MATCH_SCHEMA.parent))
        try:
            from match_schema import classify, parse_sql_signature  # type: ignore

            sigs = [parse_sql_signature(V3_2_SCHEMA_SQL, "3.2")]
            result = classify(db_path, sigs)
            best = result.get("best_match")
            if best and best["score"] < 0.8:
                raise SystemExit(
                    f"Preflight failed: database does not look like a v3.2 schema "
                    f"(best match score {best['score']:.2f}). Aborting."
                )
            logger.debug(
                f"Structural match score against v3.2: {best['score'] if best else 'n/a'}"
            )
        except ImportError:
            logger.warning(
                "match_schema module found but could not be imported; "
                "falling back to MetaData version check."
            )
        finally:
            sys.path.pop(0)

    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT element, value FROM MetaData WHERE element IN ('DB_MAJOR', 'DB_MINOR')"
        ).fetchall()
        meta = {r[0]: int(r[1]) for r in rows}
        major, minor = meta.get("DB_MAJOR"), meta.get("DB_MINOR")
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
# Collapse tables (drop `period` from the primary key)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CollapseTable:
    old_table: str
    new_table: str
    old_cols: tuple[str, ...]   # full old column list, in source order
    rename_map: dict[str, str]  # old_col -> new_col (only for renamed cols)
    dropped_cols: tuple[str, ...]  # old cols with no destination column
    pk_group_cols: tuple[str, ...]  # old-name columns forming the NEW primary key
    measure_col: str            # numeric column averaged/compared under --collapse-policy


_DQ_COLS = ("dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time")

COLLAPSE_TABLES: tuple[CollapseTable, ...] = (
    CollapseTable(
        old_table="CapacityFactorProcess", new_table="capacity_factor_process",
        old_cols=("region", "period", "season", "tod", "tech", "vintage", "factor",
                   "notes", "data_source", *_DQ_COLS, "data_id"),
        rename_map={}, dropped_cols=("period",),
        pk_group_cols=("region", "season", "tod", "tech", "vintage", "data_id"),
        measure_col="factor",
    ),
    CollapseTable(
        old_table="CapacityFactorTech", new_table="capacity_factor_tech",
        old_cols=("region", "period", "season", "tod", "tech", "factor",
                   "notes", "data_source", *_DQ_COLS, "data_id"),
        rename_map={}, dropped_cols=("period",),
        pk_group_cols=("region", "season", "tod", "tech", "data_id"),
        measure_col="factor",
    ),
    CollapseTable(
        old_table="LimitSeasonalCapacityFactor", new_table="limit_seasonal_capacity_factor",
        old_cols=("region", "period", "season", "tech", "operator", "factor",
                   "notes", "data_source", *_DQ_COLS, "data_id"),
        rename_map={"tech": "tech_or_group"}, dropped_cols=("period",),
        pk_group_cols=("region", "season", "tech", "operator", "data_id"),
        measure_col="factor",
    ),
    CollapseTable(
        old_table="LimitStorageLevelFraction", new_table="limit_storage_level_fraction",
        old_cols=("region", "period", "season", "tod", "tech", "vintage", "operator",
                   "fraction", "notes", "data_source", *_DQ_COLS, "data_id"),
        rename_map={}, dropped_cols=("period", "vintage"),
        pk_group_cols=("region", "season", "tod", "tech", "operator", "data_id"),
        measure_col="fraction",
    ),
    CollapseTable(
        old_table="ReserveCapacityDerate", new_table="reserve_capacity_derate",
        old_cols=("region", "period", "season", "tech", "vintage", "factor",
                   "notes", "data_source", *_DQ_COLS, "data_id"),
        rename_map={}, dropped_cols=("period",),
        pk_group_cols=("region", "season", "tech", "vintage", "data_id"),
        measure_col="factor",
    ),
)


def _migrate_collapse_table(
    cur: sqlite3.Cursor, table: CollapseTable, policy: CollapsePolicy
) -> None:
    total = cur.execute(f'SELECT COUNT(*) FROM src."{table.old_table}"').fetchone()[0]
    if total == 0:
        logger.info(f"{table.old_table} is empty — skipping (0 rows).")
        return

    partition_sql = ", ".join(f'"{c}"' for c in table.pk_group_cols)

    groups = cur.execute(
        f'SELECT {partition_sql}, COUNT(*) AS n, COUNT(DISTINCT "{table.measure_col}") AS ndistinct '
        f'FROM src."{table.old_table}" GROUP BY {partition_sql} HAVING n > 1'
    ).fetchall()
    n_collapsed_groups = len(groups)
    real_conflicts = [g for g in groups if g[-1] > 1]

    dropped_desc = " and ".join(f"'{c}'" for c in table.dropped_cols)
    if n_collapsed_groups:
        logger.warning(
            f"{table.old_table} -> {table.new_table}: dropping {dropped_desc} from the "
            f"primary key collapses {n_collapsed_groups} group(s) of previously-distinct "
            f"rows into one row each."
        )
    if real_conflicts:
        logger.warning(
            f"{table.old_table}: {len(real_conflicts)} of those group(s) have DIFFERING "
            f"'{table.measure_col}' values across periods — this is a genuine data conflict, "
            f"not just duplicate rows. Example key(s): {[g[:-2] for g in real_conflicts[:5]]}"
        )
        if policy == CollapsePolicy.ERROR:
            raise SystemExit(
                f"Migration aborted: {table.old_table} has {len(real_conflicts)} conflicting "
                f"group(s) after dropping {dropped_desc} from the primary key. Re-run with "
                f"--collapse-policy {{keep-earliest,keep-latest,average}} to resolve, or "
                f"edit the source data first."
            )
        logger.warning(
            f"Resolving {table.old_table} conflicts using --collapse-policy={policy.value}. "
            f"The dropped dimension ({dropped_desc}) is being discarded for this table — "
            f"review the migrated {table.new_table} rows before trusting model results "
            f"that depend on it."
        )
    elif n_collapsed_groups:
        logger.info(
            f"{table.old_table}: all collapsed groups had identical '{table.measure_col}' values. "
            f"Non-measure columns (notes/provenance) may still differ across periods and will be taken "
            f"from the selected row per --collapse-policy (earliest unless keep-latest was requested)."
        )

    order_dir = "DESC" if policy == CollapsePolicy.KEEP_LATEST else "ASC"
    select_exprs = []
    insert_cols = []
    for oc in table.old_cols:
        if oc in table.dropped_cols:
            continue
        nc = table.rename_map.get(oc, oc)
        insert_cols.append(nc)
        if policy == CollapsePolicy.AVERAGE and oc == table.measure_col:
            select_exprs.append(f'AVG("{oc}") OVER (PARTITION BY {partition_sql}) AS "{nc}"')
        elif nc != oc:
            select_exprs.append(f'"{oc}" AS "{nc}"')
        else:
            select_exprs.append(f'"{oc}"')

    insert_cols_sql = ", ".join(f'"{c}"' for c in insert_cols)
    sql = f"""
        WITH ranked AS (
            SELECT {", ".join(select_exprs)},
                   ROW_NUMBER() OVER (
                       PARTITION BY {partition_sql} ORDER BY "period" {order_dir}
                   ) AS __rn
            FROM src."{table.old_table}"
        )
        INSERT INTO "{table.new_table}" ({insert_cols_sql})
        SELECT {insert_cols_sql} FROM ranked WHERE __rn = 1
    """
    cur.execute(sql)
    inserted = _changes(cur)
    logger.info(
        f"{table.old_table} -> {table.new_table}: {total} source row(s) -> {inserted} row(s) "
        f"({total - inserted} collapsed)."
    )


# ---------------------------------------------------------------------------
# time_of_day / time_season / time_season_sequential
# ---------------------------------------------------------------------------

def _migrate_time_of_day(cur: sqlite3.Cursor) -> None:
    """
    v4.0 adds time_of_day.hours (NOT NULL, no meaningful default). v3.2 has no
    equivalent field at all, so every row is defaulted to 1.0 -- this is very
    likely wrong for any model with non-uniform tod segmentation.
    """
    cur.execute(
        'INSERT INTO "time_of_day" ("sequence", "tod", "hours") '
        'SELECT "sequence", "tod", 1.0 FROM src."TimeOfDay"'
    )
    n = _changes(cur)
    if n:
        logger.warning(
            f"time_of_day.hours has NO equivalent field in v3.2 and was defaulted to 1.0 "
            f"for all {n} time-of-day slice(s). This is almost certainly wrong for anything "
            f"other than a uniform tod segmentation — you MUST review and correct these "
            f"values by hand before trusting any tod-weighted model output."
        )


def _migrate_time_season(cur: sqlite3.Cursor, policy: CollapsePolicy) -> None:
    """
    v3.2's TimeSegmentFraction (period, season, tod, segfrac) has no v4.0
    counterpart. v4.0's time_season.segment_fraction is season-only (no
    period, no tod) — computed here as each season's share of the year,
    summing segfrac across tod for one reference period (chosen via
    --collapse-policy if it varies across periods), then normalized to sum
    to 1 across all seasons.
    """
    season_rows = cur.execute(
        'SELECT season, sequence, notes FROM src."TimeSeason" GROUP BY season, sequence, notes'
    ).fetchall()
    variability = cur.execute(
        'SELECT season, COUNT(DISTINCT sequence) n_seq, COUNT(DISTINCT notes) n_notes '
        'FROM src."TimeSeason" GROUP BY season HAVING n_seq > 1 OR n_notes > 1'
    ).fetchall()
    if variability:
        logger.warning(
            f"TimeSeason.sequence/notes vary across periods for season(s) "
            f"{[r[0] for r in variability]} — using the earliest period's value for each."
        )
    seq_and_notes: dict[str, tuple] = {}
    for season, sequence, notes in cur.execute(
        'SELECT season, sequence, notes FROM src."TimeSeason" ss '
        'WHERE period = (SELECT MIN(period) FROM src."TimeSeason" WHERE season = ss.season)'
    ).fetchall():
        seq_and_notes[season] = (sequence, notes)

    total_segfrac_rows = cur.execute('SELECT COUNT(*) FROM src."TimeSegmentFraction"').fetchone()[0]
    if total_segfrac_rows == 0:
        seasons = list(seq_and_notes) or [r[0] for r in season_rows]
        logger.warning(
            "Source has no TimeSegmentFraction data — time_season.segment_fraction cannot "
            f"be computed. Defaulting to an EQUAL split across all {len(seasons)} season(s) "
            "(1 / n each). This is almost certainly wrong; review and correct manually."
        )
        n = len(seasons) or 1
        for season in seasons:
            sequence, notes = seq_and_notes.get(season, (None, None))
            cur.execute(
                'INSERT INTO "time_season" ("sequence", "season", "segment_fraction", "notes") '
                "VALUES (?, ?, ?, ?)",
                (sequence, season, 1.0 / n, notes),
            )
        return

    per_period_season = cur.execute(
        'SELECT period, season, SUM(segfrac) AS total_frac '
        'FROM src."TimeSegmentFraction" GROUP BY period, season'
    ).fetchall()
    by_season: dict[str, dict[int, float]] = {}
    for period, season, frac in per_period_season:
        by_season.setdefault(season, {})[period] = frac

    diverging = {s: v for s, v in by_season.items() if len(set(v.values())) > 1}
    if diverging:
        examples = {s: diverging[s] for s in list(diverging)[:3]}
        logger.warning(
            f"TimeSegmentFraction's season-level totals (summed across tod) vary across "
            f"periods for {len(diverging)} season(s): {list(diverging.keys())}. v4.0's "
            f"time_season table has no period dimension, so a single value per season must "
            f"be chosen. Example totals by period: {examples}"
        )
        if policy == CollapsePolicy.ERROR:
            raise SystemExit(
                "Migration aborted: time_season.segment_fraction cannot be derived "
                "unambiguously because TimeSegmentFraction varies by period. Re-run with "
                "--collapse-policy {keep-earliest,keep-latest,average} to resolve."
            )
        logger.warning(f"Resolving with --collapse-policy={policy.value}.")

    resolved: dict[str, float] = {}
    for season, period_values in by_season.items():
        if policy == CollapsePolicy.AVERAGE:
            resolved[season] = sum(period_values.values()) / len(period_values)
        elif policy == CollapsePolicy.KEEP_LATEST:
            resolved[season] = period_values[max(period_values)]
        else:  # ERROR (no divergence reached this point) or KEEP_EARLIEST
            resolved[season] = period_values[min(period_values)]

    total_frac = sum(resolved.values()) or 1.0
    if abs(total_frac - 1.0) > 1e-6:
        logger.warning(
            f"Season fractions derived from TimeSegmentFraction sum to {total_frac:.4f}, "
            f"not 1.0. Normalizing so all seasons sum to 1 — verify this matches your "
            f"intended seasonal weighting; a non-1.0 total in the source usually means "
            f"segfrac already encoded something other than a pure season share (e.g. it was "
            f"also weighted by tod)."
        )

    for season, frac in resolved.items():
        sequence, notes = seq_and_notes.get(season, (None, None))
        cur.execute(
            'INSERT INTO "time_season" ("sequence", "season", "segment_fraction", "notes") '
            "VALUES (?, ?, ?, ?)",
            (sequence, season, frac / total_frac, notes),
        )
    logger.info(
        f"time_season.segment_fraction computed for {len(resolved)} season(s) from "
        f"TimeSegmentFraction using --collapse-policy={policy.value}. VERIFY these values "
        f"— this is a best-effort reduction of a (period, season, tod) table into a "
        f"season-only one."
    )


def _migrate_time_season_sequential(
    cur: sqlite3.Cursor, days_per_period: int, policy: CollapsePolicy
) -> None:
    """
    v4.0 replaces num_days with segment_fraction = num_days / days_per_period.
    v3.2's TimeSeasonSequential is period-scoped; v4.0's is seas_seq-only, so
    num_days must be resolved to one value per seas_seq (via --collapse-policy
    if it varies across periods).
    """
    rows = cur.execute(
        'SELECT seas_seq, sequence, season, num_days, period FROM src."TimeSeasonSequential"'
    ).fetchall()
    if not rows:
        logger.warning(
            "Source has no TimeSeasonSequential data — time_season_sequential will be empty."
        )
        return

    by_seas_seq: dict[str, dict[int, tuple]] = {}
    for seas_seq, sequence, season, num_days, period in rows:
        by_seas_seq.setdefault(seas_seq, {})[period] = (sequence, season, num_days)

    diverging = {
        k: v for k, v in by_seas_seq.items() if len({vv[2] for vv in v.values()}) > 1
    }
    if diverging:
        logger.warning(
            f"TimeSeasonSequential.num_days varies across periods for {len(diverging)} "
            f"seas_seq value(s): {list(diverging.keys())[:5]}. v4.0's time_season_sequential "
            f"has no period dimension, so a single value must be chosen."
        )
        if policy == CollapsePolicy.ERROR:
            raise SystemExit(
                "Migration aborted: time_season_sequential.segment_fraction cannot be "
                "derived unambiguously because num_days varies by period. Re-run with "
                "--collapse-policy {keep-earliest,keep-latest,average} to resolve."
            )
        logger.warning(f"Resolving with --collapse-policy={policy.value}.")

    for seas_seq, period_values in by_seas_seq.items():
        periods = sorted(period_values)
        if policy == CollapsePolicy.AVERAGE:
            num_days = sum(v[2] for v in period_values.values()) / len(period_values)
            sequence, season, _ = period_values[periods[0]]
        elif policy == CollapsePolicy.KEEP_LATEST:
            sequence, season, num_days = period_values[periods[-1]]
        else:
            sequence, season, num_days = period_values[periods[0]]

        segment_fraction = num_days / days_per_period
        cur.execute(
            'INSERT INTO "time_season_sequential" '
            '("sequence", "seas_seq", "season", "segment_fraction", "notes") '
            "VALUES (?, ?, ?, ?, NULL)",
            (sequence, seas_seq, season, segment_fraction),
        )
    logger.info(
        f"time_season_sequential.segment_fraction computed for {len(by_seas_seq)} seas_seq "
        f"value(s) as num_days / days_per_period ({days_per_period}), using "
        f"--collapse-policy={policy.value} where num_days diverged across periods."
    )


# ---------------------------------------------------------------------------
# Metadata (version already handled by schema creation; rates need a policy)
# ---------------------------------------------------------------------------

def _migrate_metadata(
    cur: sqlite3.Cursor,
    discount_policy: DiscountRatePolicy,
    days_per_period_override: int | None,
) -> int:
    """
    Copy MetaData (excluding DB_MAJOR/DB_MINOR, already set to 4/0 by schema
    creation, and days_per_period, which has no home in v4.0). Apply the
    discount-rate policy to MetaDataReal. Returns the days_per_period value
    to use for time_season_sequential's segment_fraction calculation.
    """
    cur.execute(
        'INSERT OR IGNORE INTO "metadata" ("element", "value", "notes") '
        "SELECT \"element\", \"value\", \"notes\" FROM src.\"MetaData\" "
        "WHERE \"element\" NOT IN ('DB_MAJOR', 'DB_MINOR', 'days_per_period')"
    )

    row = cur.execute(
        "SELECT value FROM src.\"MetaData\" WHERE element = 'days_per_period'"
    ).fetchone()
    source_days = int(row[0]) if row else None

    if days_per_period_override is not None:
        days_per_period = days_per_period_override
        logger.warning(
            f"--days-per-period={days_per_period} explicitly overrides the source "
            f"database's recorded value ({source_days if source_days is not None else 'unset'}). "
            f"Used only to compute time_season_sequential.segment_fraction "
            f"(= num_days / days_per_period); v4.0 no longer stores this metadata field."
        )
    elif source_days is not None:
        days_per_period = source_days
        logger.info(
            f"Using source database's days_per_period={days_per_period} to compute "
            f"time_season_sequential.segment_fraction. This MetaData row is dropped from "
            f"the v4.0 output after being consumed for this calculation."
        )
    else:
        days_per_period = DEFAULT_DAYS_PER_PERIOD
        logger.warning(
            f"Source database has no 'days_per_period' MetaData row — defaulting to "
            f"{DEFAULT_DAYS_PER_PERIOD} to compute time_season_sequential.segment_fraction. "
            f"Pass --days-per-period to override if your model uses a different convention."
        )

    source_rates = dict(
        cur.execute(
            "SELECT element, value FROM src.\"MetaDataReal\" "
            "WHERE element IN ('global_discount_rate', 'default_loan_rate')"
        ).fetchall()
    )

    if discount_policy == DiscountRatePolicy.KEEP:
        for element, value in source_rates.items():
            cur.execute(
                'REPLACE INTO "metadata_real" ("element", "value", "notes") VALUES (?, ?, ?)',
                (element, value, "Preserved from source v3.2 database by migration"),
            )
        logger.warning(
            f"Keeping the source database's economic rates unchanged: {source_rates}. "
            f"v4.0's new schema default is 0.05 for both global_discount_rate and "
            f"default_loan_rate — pass --discount-rate adopt-v4-default if you want the "
            f"migrated database to use the new default instead."
        )
    else:
        logger.warning(
            f"Overwriting economic rates with v4.0's new defaults (0.05 / 0.05) per "
            f"--discount-rate adopt-v4-default. The source database's values "
            f"({source_rates}) are being DISCARDED. This will change levelized costs and "
            f"investment decisions if the model is re-run — make sure that's intended."
        )

    return days_per_period


# ---------------------------------------------------------------------------
# Tech / tech-group namespace collision check
# ---------------------------------------------------------------------------

def _check_tech_group_collisions(
    cur: sqlite3.Cursor, policy: TechGroupCollisionPolicy
) -> None:
    """
    limit_annual_capacity_factor and limit_seasonal_capacity_factor now use a
    single `tech_or_group` column that can reference either a technology or a
    tech group. If a name exists in BOTH namespaces, any `tech_or_group` value
    equal to that name is ambiguous downstream. This is the exact concern
    already flagged in NOTES.md about TechnologyLabel/TechGroupLabel overlap.
    """
    rows = cur.execute(
        'SELECT t."tech" FROM "technology_label" t '
        'INNER JOIN "tech_group_label" g ON g."group_name" = t."tech"'
    ).fetchall()
    if not rows:
        logger.info("No naming collisions between technology_label and tech_group_label.")
        return

    names = [r[0] for r in rows]
    message = (
        f"{len(names)} name(s) exist in BOTH technology_label and tech_group_label: "
        f"{names[:10]}{' …' if len(names) > 10 else ''}. Any 'tech_or_group' value equal to "
        f"one of these names is ambiguous in limit_annual_capacity_factor and "
        f"limit_seasonal_capacity_factor — this is the open namespace question already "
        f"flagged in NOTES.md."
    )
    if policy == TechGroupCollisionPolicy.ERROR:
        raise SystemExit(
            f"Migration aborted: {message} Rename the conflicting technology or tech group "
            f"before migrating, or re-run with --tech-group-collision warn to proceed anyway."
        )
    logger.warning(message)


# ---------------------------------------------------------------------------
# Core migration runner
# ---------------------------------------------------------------------------

def _run_static_migration_sql(conn: sqlite3.Connection) -> None:
    sql = MIGRATION_SQL.read_text(encoding="utf-8")
    cur = conn.cursor()
    for chunk in sql.split(";"):
        # Strip full-line comments *before* checking for emptiness -- a chunk
        # that starts with a comment block followed by real SQL must not be
        # discarded just because its first line is a comment.
        lines = [ln for ln in chunk.splitlines() if not ln.strip().startswith("--")]
        clean = "\n".join(lines).strip()
        if clean:
            cur.execute(clean)


def migrate(
    source_path: Path,
    output_path: Path,
    collapse_policy: CollapsePolicy,
    discount_policy: DiscountRatePolicy,
    tech_group_policy: TechGroupCollisionPolicy,
    days_per_period_override: int | None,
    force: bool,
    dry_run: bool,
) -> None:
    _preflight(source_path)

    if output_path.exists() and not force:
        raise SystemExit(
            f"Output path already exists: {output_path}. Pass --force to overwrite, or "
            f"choose a different --output path."
        )
    if dry_run:
        logger.warning("Dry run enabled — no output file will be created or written to.")
        conn = sqlite3.connect(":memory:")
    else:
        if output_path.exists():
            logger.warning(f"--force set: removing existing {output_path}.")
            output_path.unlink()
        conn = sqlite3.connect(str(output_path))

    try:
        logger.info(f"Creating v4.0 schema at {output_path if not dry_run else '(in-memory)'} …")
        conn.executescript(V4_0_SCHEMA_SQL.read_text(encoding="utf-8"))

        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("ATTACH DATABASE ? AS src", (str(source_path),))
        conn.execute("BEGIN")
        cur = conn.cursor()

        logger.info("Phase 3: static table copies (pure renames / additions) …")
        _run_static_migration_sql(conn)

        logger.info("Phase 4: collapsing tables that drop 'period' from the primary key …")
        for table in COLLAPSE_TABLES:
            _migrate_collapse_table(cur, table, collapse_policy)

        logger.info("Phase 5: time tables (time_of_day, time_season, time_season_sequential) …")
        _migrate_time_of_day(cur)
        days_per_period = _migrate_metadata(cur, discount_policy, days_per_period_override)
        _migrate_time_season(cur, collapse_policy)
        _migrate_time_season_sequential(cur, days_per_period, collapse_policy)

        logger.info("Phase 6: tech / tech-group namespace collision check …")
        _check_tech_group_collisions(cur, tech_group_policy)

        if dry_run:
            logger.warning("Dry run complete — rolling back (nothing was written to disk).")
            conn.rollback()
        else:
            conn.commit()
            conn.execute("PRAGMA foreign_keys = ON")
            fk_violations = conn.execute("PRAGMA foreign_key_check").fetchall()
            if fk_violations:
                logger.error(
                    f"{len(fk_violations)} foreign-key violation(s) found in the migrated "
                    f"database — inspect {output_path} before using it. First few: "
                    f"{fk_violations[:5]}"
                )
            else:
                logger.success("Foreign-key check passed: no violations found.")
            logger.success(f"Migration committed successfully to {output_path}.")

    except (Exception, SystemExit) as exc:
        # SystemExit (raised by every abort path above -- collapse conflicts,
        # tech-group collisions, etc.) is a BaseException, NOT an Exception,
        # so it must be caught explicitly here too or this cleanup never runs.
        conn.rollback()
        conn.close()
        if not dry_run and output_path.exists():
            output_path.unlink()
            logger.info(f"Removed incomplete output file: {output_path}.")
        logger.info(f"Source database is untouched: {source_path}.")
        if isinstance(exc, SystemExit):
            raise
        logger.error(f"Migration failed. Reason: {exc}")
        raise SystemExit(1) from exc

    conn.close()

    if not dry_run:
        logger.success(
            f"Database '{source_path}' has been migrated to schema v4.0 at '{output_path}'.\n"
            f"The source database was never modified."
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
        description="Migrate a CANOE SQLite database from schema v3.2 to v4.0.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("sqlite_db", type=Path, help="Path to the source v3.2 SQLite database.")
    parser.add_argument(
        "--output", type=Path, default=None,
        help="Path for the new v4.0 database (default: <name>.v4_0.db next to the source).",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Overwrite --output if it already exists.",
    )
    parser.add_argument(
        "--collapse-policy",
        choices=[p.value for p in CollapsePolicy],
        default=CollapsePolicy.ERROR.value,
        dest="collapse_policy",
        help=(
            "How to resolve tables/computations that drop 'period' as a dimension "
            "(capacity_factor_process/tech, limit_seasonal_capacity_factor, "
            "limit_storage_level_fraction, reserve_capacity_derate, and the "
            "time_season/time_season_sequential segment_fraction calculations). "
            "'error' (default): abort if values genuinely differ across periods. "
            "'keep-earliest'/'keep-latest': use the earliest/latest period's row. "
            "'average': average the numeric measure across periods."
        ),
    )
    parser.add_argument(
        "--discount-rate",
        choices=[p.value for p in DiscountRatePolicy],
        default=DiscountRatePolicy.KEEP.value,
        dest="discount_rate",
        help=(
            "'keep' (default): preserve the source database's global_discount_rate / "
            "default_loan_rate values. 'adopt-v4-default': overwrite with v4.0's new "
            "0.05 / 0.05 defaults."
        ),
    )
    parser.add_argument(
        "--tech-group-collision",
        choices=[p.value for p in TechGroupCollisionPolicy],
        default=TechGroupCollisionPolicy.WARN.value,
        dest="tech_group_collision",
        help=(
            "'warn' (default): log a warning if a name exists in both the technology "
            "and tech-group namespaces. 'error': abort the migration instead."
        ),
    )
    parser.add_argument(
        "--days-per-period", type=int, default=None, dest="days_per_period",
        help=(
            "Override the days-per-period used to compute "
            "time_season_sequential.segment_fraction (default: read from the source "
            "database's MetaData, falling back to 365)."
        ),
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Run all checks and log what would happen; write nothing to disk.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug-level logging.")

    args = parser.parse_args()
    _configure_logging(args.verbose)

    source_path = args.sqlite_db.resolve()
    if not source_path.exists():
        logger.error(f"Database file not found: {source_path}")
        raise SystemExit(1)

    output_path = (
        args.output.resolve() if args.output
        else source_path.with_suffix(".v4_0.db")
    )

    migrate(
        source_path=source_path,
        output_path=output_path,
        collapse_policy=CollapsePolicy(args.collapse_policy),
        discount_policy=DiscountRatePolicy(args.discount_rate),
        tech_group_policy=TechGroupCollisionPolicy(args.tech_group_collision),
        days_per_period_override=args.days_per_period,
        force=args.force,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
