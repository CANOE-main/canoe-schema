#### v3.2 → v4.0

**Architecture note:** unlike the v3.1 → v3.2 migration, this one does **not**
modify the source file in place. Nearly every table is renamed from
CamelCase to snake_case in v4.0 (`Technology` → `technology`), and SQLite
table names are case-insensitive, so `Technology` and `technology` cannot
coexist in the same file. Instead, `migrate.py`:

1. Creates a **new** SQLite file and initializes it by executing
   `canoe_schema/v4_0/schema.sql` verbatim (so the target schema can never
   drift from the single source of truth).
2. `ATTACH`es the source v3.2 database under the alias `src`.
3. Copies every table across with the exact column mapping the two schemas
   require.
4. Runs `PRAGMA foreign_key_check` on the result before declaring success.

The source database is **never written to**. There is no `.bak` file
because there is nothing to roll back — if anything goes wrong, the
(incomplete) output file is deleted automatically and you just re-run.

**What changes automatically — no input needed:**

| Change | Detail |
|---|---|
| ~68 table/column renames | CamelCase → snake_case, executed via `migrate.sql` |
| Enum/seed tables | `commodity_type`, `technology_type`, `time_period_type`, `operator`, `data_quality_*` — fixed rows, `INSERT OR IGNORE` so any custom extra rows in the source survive |
| New `tech_group_label` | Backfilled from `DISTINCT group_name` in `TechGroup`, same pattern as the v3.1→v3.2 label tables |
| `tech`→`tech_or_group`, `period`→`vintage` renames | `limit_annual_capacity_factor`, `limit_new_capacity`, `limit_new_capacity_share` — lossless, row count unchanged |
| `rps_requirement` PK widening | `(region, data_id)` → `(region, period, tech_group, data_id)` — strictly safe; v3.2's tighter PK meant only one row per `(region, data_id)` could ever exist |
| New nullable columns (`units`, `linked_tech.data_source`) | Left `NULL`, no source data to carry over |

**What needs a policy decision (all have a sensible default + a loud warning):**

| Flag | Default | Applies to |
|---|---|---|
| `--collapse-policy {error,keep-earliest,keep-latest,average}` | `error` | Tables/computations that drop `period` as a dimension: `capacity_factor_process`, `capacity_factor_tech`, `limit_seasonal_capacity_factor`, `limit_storage_level_fraction`, `reserve_capacity_derate`, plus the `time_season`/`time_season_sequential` `segment_fraction` calculations. `error` only aborts when values **genuinely differ** across periods for the same remaining key — harmless duplicate rows (identical values at every period) always collapse silently. |
| `--discount-rate {keep,adopt-v4-default}` | `keep` | `metadata_real.global_discount_rate` / `default_loan_rate`. v4.0's schema default changed from 0.03 to 0.05; `keep` preserves whatever the source database was actually calibrated to. |
| `--tech-group-collision {warn,error}` | `warn` | Checks whether any name exists in both `technology_label` and `tech_group_label` — such a name is ambiguous wherever `tech_or_group` is used (see `NOTES.md`). |
| `--days-per-period N` | auto (from source `MetaData`, else 365) | Used only to compute `time_season_sequential.segment_fraction = num_days / days_per_period`; the metadata field itself has no home in v4.0 and is dropped after being consumed. |
| `--backfill-labels` | off | Backfills `commodity_label`, `technology_label`, `sector_label`, `data_source_label` from the values actually present in the migrated `commodity`/`technology`/`data_source` tables — catches any name used in the source data but never registered in its v3.2 label table. Off by default: without it, such gaps surface later as `PRAGMA foreign_key_check` violations instead. |

**Always logged as a loud warning, no flag (nothing to decide, just no source data):**

- `time_of_day.hours` — v3.2 has no equivalent field at all; every row is defaulted to `1.0`. Review and correct manually before trusting any tod-weighted output.
- `time_season.segment_fraction` — derived from v3.2's now-dropped `TimeSegmentFraction` by summing `segfrac` across `tod` for one reference period, then normalizing across seasons. This is a best-effort reduction of a `(period, season, tod)` table into a season-only one — verify the results.

**Usage:**

```bash
python canoe_schema/v3_2/migrations/to_v4_0/migrate.py path/to/database.db
# writes path/to/database.v4_0.db by default
```

**Options:**

| Flag | Default | Description |
|---|---|---|
| `--output PATH` | `<name>.v4_0.db` next to the source | Where to write the migrated database |
| `--force` | | Overwrite `--output` if it already exists |
| `--collapse-policy` | `error` | See table above |
| `--discount-rate` | `keep` | See table above |
| `--tech-group-collision` | `warn` | See table above |
| `--days-per-period N` | auto | See table above |
| `--backfill-labels` | off | See table above |
| `--dry-run` | | Run all checks and log every decision; write nothing to disk |
| `-v / --verbose` | | Enable debug-level logging |

**Examples:**

```bash
# Default: abort if any dropped-period table has genuinely conflicting values
python canoe_schema/v3_2/migrations/to_v4_0/migrate.py my_model.db

# Resolve conflicts by keeping the most recent period's value, adopt v4.0's new discount rate
python canoe_schema/v3_2/migrations/to_v4_0/migrate.py my_model.db \
    --collapse-policy keep-latest --discount-rate adopt-v4-default

# Preview every decision the migration would make, without writing anything
python canoe_schema/v3_2/migrations/to_v4_0/migrate.py my_model.db --dry-run --verbose
```
