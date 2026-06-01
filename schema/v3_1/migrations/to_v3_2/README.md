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
