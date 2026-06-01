# CANOE Schema

This repository manages the versioned SQLite database schemas for the CANOE energy
systems model, along with Pydantic models that mirror each schema version and tooling
for schema identification and database migration.

## Repository Structure

```
.
├── schema/
│   ├── v3_1/
│   │   ├── schema_3_1.sql          # Schema DDL
│   │   ├── models.py               # Pydantic models (in sync with DDL)
│   │   └── migrations/
│   │       └── to_v3_2/
│   │           ├── migrate.py      # Migration orchestrator (CLI)
│   │           ├── migrate.sql     # Raw SQL executed by migrate.py
│   │           └── README.md       # Migration-specific notes
│   └── v3_2/
│       ├── canoe_schema.sql
│       └── models.py
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
python schema/v3_1/migrations/to_v3_2/migrate.py path/to/database.db
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
python schema/v3_1/migrations/to_v3_2/migrate.py my_model.db

# Automatically resolve duplicates by keeping the most-referenced entry
python schema/v3_1/migrations/to_v3_2/migrate.py my_model.db --duplicate-tech fix

# Preview what the migration would do without touching the database
python schema/v3_1/migrations/to_v3_2/migrate.py my_model.db --dry-run --verbose
```

**Backup:**

Before applying any changes the script creates a backup at
`<original_name>.v3_1.bak` in the same directory. If the migration fails for
any reason the database is rolled back to its original state and the backup is
preserved for reference.

## Adding a New Migration

1. Create `schema/vX_Y/migrations/to_vX_Z/`.
2. Add `migrate.sql` with the raw DDL/DML changes.
3. Add `migrate.py` as the CLI orchestrator (preflight, user interaction, transaction
   management).
4. Add a `README.md` documenting what changed and any manual review steps.
5. Update this file with the new migration entry.
