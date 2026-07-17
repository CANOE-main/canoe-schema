-- =============================================================================
-- Migration: v3.1 → v3.2
-- Phases:
--   1. Populate new global label tables (TechnologyLabel, CommodityLabel,
--      DataSourceLabel)
--   2. Duplicate tech resolution is handled in migrate.py before this runs.
--      This phase assumes the caller has already resolved conflicts and
--      passed the set of (tech, data_id) pairs to retain.
--   3. LimitAnnualCapacityFactor: drop period column, add vintage column.
--   4. Seed TimePeriod with canonical 3.2 values (upsert).
--   5. Add new FK-enforcing label tables and update MetaData version.
-- =============================================================================

-- ── Phase 1: Create and populate global label tables ─────────────────────────

CREATE TABLE IF NOT EXISTS TechnologyLabel
(
    tech  TEXT PRIMARY KEY,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS CommodityLabel
(
    commodity TEXT PRIMARY KEY,
    notes     TEXT
);

CREATE TABLE IF NOT EXISTS DataSourceLabel
(
    source_id TEXT PRIMARY KEY,
    notes     TEXT
);

INSERT OR IGNORE INTO TechnologyLabel (tech)
SELECT DISTINCT tech FROM Technology;

INSERT OR IGNORE INTO CommodityLabel (commodity)
SELECT DISTINCT name FROM Commodity;

INSERT OR IGNORE INTO DataSourceLabel (source_id)
SELECT DISTINCT source_id FROM DataSource;

-- ── Phase 3: Migrate LimitAnnualCapacityFactor ───────────────────────────────
-- The 3.2 schema replaces `period` with `vintage` in this table.
-- We migrate by setting vintage = period for all existing rows as a best-effort
-- default. The orchestrator logs a warning about this before running.

CREATE TABLE IF NOT EXISTS LimitAnnualCapacityFactor_new
(
    region      TEXT,
    tech        TEXT,
    vintage     INTEGER
        REFERENCES TimePeriod (period),
    output_comm TEXT,
    operator    TEXT NOT NULL DEFAULT "le"
        REFERENCES Operator (operator),
    factor      REAL,
    notes       TEXT,
    data_source TEXT,
    dq_cred     INTEGER REFERENCES DataQualityCredibility (dq_cred),
    dq_geog     INTEGER REFERENCES DataQualityGeography (dq_geog),
    dq_struc    INTEGER REFERENCES DataQualityStructure (dq_struc),
    dq_tech     INTEGER REFERENCES DataQualityTechnology (dq_tech),
    dq_time     INTEGER REFERENCES DataQualityTime (dq_time),
    data_id     TEXT REFERENCES DataSet (data_id),
    FOREIGN KEY (data_source) REFERENCES DataSourceLabel (source_id),
    FOREIGN KEY (tech) REFERENCES TechnologyLabel (tech),
    FOREIGN KEY (output_comm) REFERENCES CommodityLabel (commodity),
    PRIMARY KEY (region, tech, vintage, output_comm, operator, data_id),
    CHECK (factor >= 0 AND factor <= 1)
);

INSERT OR IGNORE INTO LimitAnnualCapacityFactor_new
    (region, tech, vintage, output_comm, operator, factor, notes,
     data_source, dq_cred, dq_geog, dq_struc, dq_tech, dq_time, data_id)
SELECT
    region, tech, period, output_comm, operator, factor, notes,
    data_source, dq_cred, dq_geog, dq_struc, dq_tech, dq_time, data_id
FROM LimitAnnualCapacityFactor;

DROP TABLE LimitAnnualCapacityFactor;

ALTER TABLE LimitAnnualCapacityFactor_new
    RENAME TO LimitAnnualCapacityFactor;

-- ── Phase 4: Seed TimePeriod (upsert) ────────────────────────────────────────

-- REPLACE INTO TimePeriod (sequence, period, flag) VALUES (0, 2025, 'f');
-- REPLACE INTO TimePeriod (sequence, period, flag) VALUES (1, 2030, 'f');
-- REPLACE INTO TimePeriod (sequence, period, flag) VALUES (2, 2035, 'f');
-- REPLACE INTO TimePeriod (sequence, period, flag) VALUES (3, 2040, 'f');
-- REPLACE INTO TimePeriod (sequence, period, flag) VALUES (4, 2045, 'f');
-- REPLACE INTO TimePeriod (sequence, period, flag) VALUES (5, 2050, 'f');

-- ── Phase 5: Update MetaData version ─────────────────────────────────────────

REPLACE INTO MetaData VALUES ('DB_MAJOR', 3, 'DB major version number');
REPLACE INTO MetaData VALUES ('DB_MINOR', 2, 'DB minor version number');
