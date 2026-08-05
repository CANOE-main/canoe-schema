# CANOE Schema

This repository manages the versioned SQLite database schemas for the CANOE energy
systems model, along with Pydantic models that mirror each schema version and tooling
for schema identification and database migration.

## Repository Structure

```
.
├── canoe_schema/                   # Pydantic models (in sync with DDL)
│   ├── v3_1/
│   │   ├── enums.py
│   │   └── models.py               
│   │   ├── schema.sql              # Schema DDL
│   │   └── migrations/
│   │       └── to_v3_2/
│   │           ├── migrate.py      # Migration orchestrator (CLI)
│   │           ├── migrate.sql     # Raw SQL executed by migrate.py
│   │           └── README.md       # Migration-specific notes
│   ├── v3_2/
│   │   ├── enums.py
│   │   ├── models.py
│   │   ├── schema.sql
│   │   └── migrations/
│   │       └── to_v4_0/
│   │           ├── migrate.py      # Migration orchestrator (CLI)
│   │           ├── migrate.sql     # Static (unconditional) table copies
│   │           └── README.md       # Migration-specific notes
│   └── v4_0/
│       ├── enums.py
│       ├── models.py
│       └── schema.sql
└── tools/
    └── match_schema.py             # Identify the schema version of a database
```

## Tools

### `match_schema.py` — Identify a database's schema version

Compares a SQLite database against all known schema versions and reports the
closest structural match. Useful as a preflight check before running migrations.

**Usage:**

```bash
python tools/match_schema.py path/to/database.db
```

**Options:**

| Flag | Description |
|---|---|
| `--format json` | Output results as JSON instead of human-readable text |
| `--diff` | Whether to show specific table-level differences between database and schema (only on text format) |

**Example output:**

```
Database: my_model.db
MetaData version keys: DB_MAJOR=3 DB_MINOR=1
Exact schema match: 3.1
Best candidate: 3.1 (score=1.0, tables 42/42)
Recommendation: Add a string schema id in a dedicated table ...
```

---

### `migrate.py` — Migrate a database between schema versions

Each migration lives alongside the source schema version it migrates *from*.
The script performs a full preflight check, creates a `.bak` backup, and runs
the entire migration in a single transaction — rolling back on any error so the
source database is never left in a partial state.

#### v3.1 → v3.2
> See `canoe_schema/<version>/migrations` for all available migrations (v3.2 → v4.0 is documented below)

**What changes:**

| Phase | Description |
|---|---|
| 1 | Populate new global label tables (`TechnologyLabel`, `CommodityLabel`, `DataSourceLabel`) |
| 2 | Detect and optionally resolve technology names duplicated across datasets |
| 3 | Migrate `LimitAnnualCapacityFactor`: replace `period` column with `vintage` |
| 4 | Upsert canonical time periods (2025–2050) into `TimePeriod` |
| 5 | Update `DB_MINOR` to `2` in `MetaData` |

**Usage:**

```bash
python canoe_schema/v3_1/migrations/to_v3_2/migrate.py path/to/database.db
```

**Options:**

| Flag | Default | Description |
|---|---|---|
| `--duplicate-tech error` | ✓ | Abort if any tech name exists in more than one dataset |
| `--duplicate-tech warn` | | Log a warning and continue without resolving duplicates |
| `--duplicate-tech fix` | | Keep the entry with the most `Efficiency` references (tiebreak: alphabetically lowest `data_id`) |
| `--dry-run` | | Run all checks and print what would happen; do not modify the database |
| `-v / --verbose` | | Enable debug-level logging |

**Examples:**

```bash
# Default: abort on duplicate technologies
python canoe_schema/v3_1/migrations/to_v3_2/migrate.py my_model.db

# Automatically resolve duplicates by keeping the most-referenced entry
python canoe_schema/v3_1/migrations/to_v3_2/migrate.py my_model.db --duplicate-tech fix

# Preview what the migration would do without touching the database
python canoe_schema/v3_1/migrations/to_v3_2/migrate.py my_model.db --dry-run --verbose
```

**Backup:**

Before applying any changes the script creates a backup at
`<original_name>.v3_1.bak` in the same directory. If the migration fails for
any reason the database is rolled back to its original state and the backup is
preserved for reference.

---

#### v3.2 → v4.0

Unlike the v3.1 → v3.2 migration, this one does **not** modify the source
file in place — nearly every table is renamed from CamelCase to snake_case
in v4.0, and SQLite table names are case-insensitive, so the old and new
names can't coexist in one file. Instead the script builds a brand-new
database from `canoe_schema/v4_0/schema.sql` and copies the source data
across via an `ATTACH`ed connection. The source database is never written
to, so there is no `.bak` file — see
`canoe_schema/v3_2/migrations/to_v4_0/README.md` for the full breakdown of
what's automatic vs. what needs a policy decision.

**What changes:**

| Phase | Description |
|---|---|
| 1 | Create the v4.0 schema in a new output file |
| 2 | Static copy of ~68 tables (pure CamelCase → snake_case renames/additions) |
| 3 | Resolve tables that drop `period` from their primary key (`capacity_factor_process/tech`, `limit_seasonal_capacity_factor`, `limit_storage_level_fraction`, `reserve_capacity_derate`) |
| 4 | Compute `time_of_day.hours`, `time_season.segment_fraction`, `time_season_sequential.segment_fraction` (no v3.2 equivalents) |
| 5 | Apply the discount/loan-rate policy and drop the now-unused `days_per_period` metadata |
| 6 | Check for naming collisions between `technology_label` and the new `tech_group_label` |
| 7 | `PRAGMA foreign_key_check` on the result |

**Usage:**

```bash
python canoe_schema/v3_2/migrations/to_v4_0/migrate.py path/to/database.db
```

**Options:**

| Flag | Default | Description |
|---|---|---|
| `--output PATH` | `<name>.v4_0.db` | Where to write the migrated database |
| `--force` | | Overwrite `--output` if it already exists |
| `--collapse-policy {error,keep-earliest,keep-latest,average}` | `error` | How to resolve genuinely conflicting values in tables that drop `period` |
| `--discount-rate {keep,adopt-v4-default}` | `keep` | Preserve the source's economic rates, or adopt v4.0's new 0.05 default |
| `--tech-group-collision {warn,error}` | `warn` | What to do if a name exists in both the technology and tech-group namespaces |
| `--days-per-period N` | auto-detected | Override for computing `time_season_sequential.segment_fraction` |
| `--dry-run` | | Run all checks and log every decision; write nothing to disk |
| `-v / --verbose` | | Enable debug-level logging |

**Examples:**

```bash
# Default: abort if any period-dropping table has genuinely conflicting values
python canoe_schema/v3_2/migrations/to_v4_0/migrate.py my_model.db

# Resolve conflicts with the latest period's value, adopt the new discount rate default
python canoe_schema/v3_2/migrations/to_v4_0/migrate.py my_model.db \
    --collapse-policy keep-latest --discount-rate adopt-v4-default

# Preview every decision the migration would make, without writing anything
python canoe_schema/v3_2/migrations/to_v4_0/migrate.py my_model.db --dry-run --verbose
```

## Adding a New Migration

1. Create `schema/vX_Y/migrations/to_vX_Z/`.
2. Add `migrate.sql` with the raw DDL/DML changes.
3. Add `migrate.py` as the CLI orchestrator (preflight, user interaction, transaction
   management).
4. Add a `README.md` documenting what changed and any manual review steps.
5. Update this file with the new migration entry.
