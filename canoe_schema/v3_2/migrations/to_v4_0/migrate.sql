-- =============================================================================
-- Migration: v3.2 -> v4.0  (static, unconditional table copies)
--
-- This file is executed by migrate.py against a brand-new database that
-- already has the full v4.0 schema created (via canoe_schema/v4_0/schema.sql)
-- and the source v3.2 database ATTACHed under the alias `src`.
--
-- Only tables that can be copied with NO policy decision live here: pure
-- CamelCase -> snake_case renames, additions of nullable columns with no
-- source equivalent, and the two safe/lossless column renames
-- (tech -> tech_or_group, period -> vintage) that don't change row counts.
--
-- Tables that need a collapse policy (dropping `period` from the primary
-- key), a discount-rate decision, or a computed value (segment_fraction,
-- tod hours) are handled separately in migrate.py so they can emit warnings
-- and honor CLI flags. See migrate.py's MIGRATED_ELSEWHERE for the full list.
-- =============================================================================

-- ── New in v4.0: tech_group_label registry, backfilled from existing group
--    names (same pattern used for technology_label/commodity_label/
--    data_source_label in the v3.1 -> v3.2 migration). ────────────────────────
INSERT OR IGNORE INTO "tech_group_label" ("group_name")
SELECT DISTINCT "group_name" FROM src."TechGroup";

-- ── Pure renames + trivial column additions ─────────────────────────────────

INSERT INTO "capacity_credit" ("region", "period", "tech", "vintage", "credit", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "period", "tech", "vintage", "credit", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."CapacityCredit";

INSERT INTO "capacity_to_activity" ("region", "tech", "c2a", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "tech", "c2a", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."CapacityToActivity";

INSERT INTO "commodity" ("name", "flag", "description", "data_id")
SELECT "name", "flag", "description", "data_id" FROM src."Commodity";

INSERT INTO "commodity_label" ("commodity", "notes")
SELECT "commodity", "notes" FROM src."CommodityLabel";

INSERT OR IGNORE INTO "commodity_type" ("label", "description")
SELECT "label", "description" FROM src."CommodityType";

INSERT INTO "construction_input" ("region", "input_comm", "tech", "vintage", "value", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "input_comm", "tech", "vintage", "value", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."ConstructionInput";

INSERT INTO "cost_emission" ("region", "period", "emis_comm", "cost", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "period", "emis_comm", "cost", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."CostEmission";

INSERT INTO "cost_fixed" ("region", "period", "tech", "vintage", "cost", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "period", "tech", "vintage", "cost", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."CostFixed";

INSERT INTO "cost_invest" ("region", "tech", "vintage", "cost", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "tech", "vintage", "cost", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."CostInvest";

INSERT INTO "cost_variable" ("region", "period", "tech", "vintage", "cost", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "period", "tech", "vintage", "cost", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."CostVariable";

INSERT OR IGNORE INTO "data_quality_credibility" ("dq_cred", "description")
SELECT "dq_cred", "description" FROM src."DataQualityCredibility";

INSERT OR IGNORE INTO "data_quality_geography" ("dq_geog", "description")
SELECT "dq_geog", "description" FROM src."DataQualityGeography";

INSERT OR IGNORE INTO "data_quality_structure" ("dq_struc", "description")
SELECT "dq_struc", "description" FROM src."DataQualityStructure";

INSERT OR IGNORE INTO "data_quality_technology" ("dq_tech", "description")
SELECT "dq_tech", "description" FROM src."DataQualityTechnology";

INSERT OR IGNORE INTO "data_quality_time" ("dq_time", "description")
SELECT "dq_time", "description" FROM src."DataQualityTime";

INSERT INTO "data_set" ("data_id", "label", "version", "description", "status", "author", "date", "parent_id", "changelog", "notes")
SELECT "data_id", "label", "version", "description", "status", "author", "date", "parent_id", "changelog", "notes" FROM src."DataSet";

INSERT INTO "data_source" ("source_id", "source", "notes", "data_id")
SELECT "source_id", "source", "notes", "data_id" FROM src."DataSource";

INSERT INTO "data_source_label" ("source_id", "notes")
SELECT "source_id", "notes" FROM src."DataSourceLabel";

INSERT INTO "demand" ("region", "period", "commodity", "demand", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "period", "commodity", "demand", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."Demand";

INSERT INTO "demand_specific_distribution" ("region", "period", "season", "tod", "demand_name", "dsd", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "period", "season", "tod", "demand_name", "dsd", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."DemandSpecificDistribution";

INSERT INTO "efficiency" ("region", "input_comm", "tech", "vintage", "output_comm", "efficiency", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "input_comm", "tech", "vintage", "output_comm", "efficiency", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."Efficiency";

INSERT INTO "efficiency_variable" ("region", "season", "tod", "input_comm", "tech", "vintage", "output_comm", "efficiency", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "season", "tod", "input_comm", "tech", "vintage", "output_comm", "efficiency", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."EfficiencyVariable";

INSERT INTO "emission_activity" ("region", "emis_comm", "input_comm", "tech", "vintage", "output_comm", "activity", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "emis_comm", "input_comm", "tech", "vintage", "output_comm", "activity", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."EmissionActivity";

INSERT INTO "emission_embodied" ("region", "emis_comm", "tech", "vintage", "value", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "emis_comm", "tech", "vintage", "value", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."EmissionEmbodied";

INSERT INTO "emission_end_of_life" ("region", "emis_comm", "tech", "vintage", "value", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "emis_comm", "tech", "vintage", "value", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."EmissionEndOfLife";

INSERT INTO "end_of_life_output" ("region", "tech", "vintage", "output_comm", "value", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "tech", "vintage", "output_comm", "value", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."EndOfLifeOutput";

INSERT INTO "existing_capacity" ("region", "tech", "vintage", "capacity", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "tech", "vintage", "capacity", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."ExistingCapacity";

INSERT INTO "lifetime_process" ("region", "tech", "vintage", "lifetime", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "tech", "vintage", "lifetime", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LifetimeProcess";

INSERT INTO "lifetime_survival_curve" ("region", "period", "tech", "vintage", "fraction", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "period", "tech", "vintage", "fraction", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LifetimeSurvivalCurve";

INSERT INTO "lifetime_tech" ("region", "tech", "lifetime", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "tech", "lifetime", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LifetimeTech";

INSERT INTO "limit_activity" ("region", "period", "tech_or_group", "operator", "activity", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "period", "tech_or_group", "operator", "activity", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LimitActivity";

INSERT INTO "limit_activity_share" ("region", "period", "sub_group", "super_group", "operator", "share", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "period", "sub_group", "super_group", "operator", "share", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LimitActivityShare";

INSERT INTO "limit_annual_capacity_factor" ("region", "tech_or_group", "vintage", "output_comm", "operator", "factor", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "tech" AS "tech_or_group", "vintage", "output_comm", "operator", "factor", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LimitAnnualCapacityFactor";

INSERT INTO "limit_capacity" ("region", "period", "tech_or_group", "operator", "capacity", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "period", "tech_or_group", "operator", "capacity", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LimitCapacity";

INSERT INTO "limit_capacity_share" ("region", "period", "sub_group", "super_group", "operator", "share", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "period", "sub_group", "super_group", "operator", "share", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LimitCapacityShare";

INSERT INTO "limit_degrowth_capacity" ("region", "tech_or_group", "operator", "rate", "seed", "seed_units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "tech_or_group", "operator", "rate", "seed", "seed_units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LimitDegrowthCapacity";

INSERT INTO "limit_degrowth_new_capacity" ("region", "tech_or_group", "operator", "rate", "seed", "seed_units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "tech_or_group", "operator", "rate", "seed", "seed_units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LimitDegrowthNewCapacity";

INSERT INTO "limit_degrowth_new_capacity_delta" ("region", "tech_or_group", "operator", "rate", "seed", "seed_units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "tech_or_group", "operator", "rate", "seed", "seed_units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LimitDegrowthNewCapacityDelta";

INSERT INTO "limit_emission" ("region", "period", "emis_comm", "operator", "value", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "period", "emis_comm", "operator", "value", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LimitEmission";

INSERT INTO "limit_growth_capacity" ("region", "tech_or_group", "operator", "rate", "seed", "seed_units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "tech_or_group", "operator", "rate", "seed", "seed_units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LimitGrowthCapacity";

INSERT INTO "limit_growth_new_capacity" ("region", "tech_or_group", "operator", "rate", "seed", "seed_units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "tech_or_group", "operator", "rate", "seed", "seed_units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LimitGrowthNewCapacity";

INSERT INTO "limit_growth_new_capacity_delta" ("region", "tech_or_group", "operator", "rate", "seed", "seed_units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "tech_or_group", "operator", "rate", "seed", "seed_units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LimitGrowthNewCapacityDelta";

-- period -> vintage: the new column takes the OLD period value verbatim.
-- This is a lossless rename of the constraint's time axis, NOT a collapse
-- (row count is unchanged). migrate.py logs a warning about this either way.
INSERT INTO "limit_new_capacity" ("region", "vintage", "tech_or_group", "operator", "new_cap", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "period" AS "vintage", "tech_or_group", "operator", "new_cap", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LimitNewCapacity";

INSERT INTO "limit_new_capacity_share" ("region", "vintage", "sub_group", "super_group", "operator", "share", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "period" AS "vintage", "sub_group", "super_group", "operator", "share", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LimitNewCapacityShare";

INSERT INTO "limit_resource" ("region", "tech_or_group", "operator", "cum_act", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "tech_or_group", "operator", "cum_act", "units", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LimitResource";

INSERT INTO "limit_tech_input_split" ("region", "period", "input_comm", "tech", "operator", "proportion", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "period", "input_comm", "tech", "operator", "proportion", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LimitTechInputSplit";

INSERT INTO "limit_tech_input_split_annual" ("region", "period", "input_comm", "tech", "operator", "proportion", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "period", "input_comm", "tech", "operator", "proportion", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LimitTechInputSplitAnnual";

INSERT INTO "limit_tech_output_split" ("region", "period", "tech", "output_comm", "operator", "proportion", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "period", "tech", "output_comm", "operator", "proportion", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LimitTechOutputSplit";

INSERT INTO "limit_tech_output_split_annual" ("region", "period", "tech", "output_comm", "operator", "proportion", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "period", "tech", "output_comm", "operator", "proportion", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LimitTechOutputSplitAnnual";

INSERT INTO "linked_tech" ("primary_region", "primary_tech", "emis_comm", "driven_tech", "notes", "data_id")
SELECT "primary_region", "primary_tech", "emis_comm", "driven_tech", "notes", "data_id" FROM src."LinkedTech";

INSERT INTO "loan_lifetime_process" ("region", "tech", "vintage", "lifetime", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "tech", "vintage", "lifetime", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LoanLifetimeProcess";

INSERT INTO "loan_rate" ("region", "tech", "vintage", "rate", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "tech", "vintage", "rate", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."LoanRate";

INSERT OR IGNORE INTO "operator" ("operator", "notes")
SELECT "operator", "notes" FROM src."Operator";

INSERT INTO "planning_reserve_margin" ("region", "margin", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "margin", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."PlanningReserveMargin";

-- PK widens from (region, data_id) to (region, period, tech_group, data_id).
-- This is strictly safe: period/tech_group were already NOT NULL in v3.2 but
-- excluded from the PK there (a latent bug -- see NOTES.md), so v3.2 could
-- only ever hold one row per (region, data_id) anyway. No data can violate
-- the new, stricter key.
INSERT INTO "rps_requirement" ("region", "period", "tech_group", "requirement", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id", "notes")
SELECT "region", "period", "tech_group", "requirement", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id", "notes" FROM src."RPSRequirement";

INSERT INTO "ramp_down_hourly" ("region", "tech", "rate", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "tech", "rate", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."RampDownHourly";

INSERT INTO "ramp_up_hourly" ("region", "tech", "rate", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "tech", "rate", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."RampUpHourly";

INSERT INTO "region" ("region", "notes")
SELECT "region", "notes" FROM src."Region";

INSERT INTO "sector_label" ("sector", "notes")
SELECT "sector", "notes" FROM src."SectorLabel";

INSERT INTO "storage_duration" ("region", "tech", "duration", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id")
SELECT "region", "tech", "duration", "notes", "data_source", "dq_cred", "dq_geog", "dq_struc", "dq_tech", "dq_time", "data_id" FROM src."StorageDuration";

INSERT INTO "tech_group" ("group_name", "notes", "data_id")
SELECT "group_name", "notes", "data_id" FROM src."TechGroup";

INSERT INTO "tech_group_member" ("group_name", "tech", "data_id")
SELECT "group_name", "tech", "data_id" FROM src."TechGroupMember";

INSERT INTO "technology" ("tech", "flag", "sector", "category", "sub_category", "unlim_cap", "annual", "reserve", "curtail", "retire", "flex", "exchange", "seas_stor", "description", "data_id")
SELECT "tech", "flag", "sector", "category", "sub_category", "unlim_cap", "annual", "reserve", "curtail", "retire", "flex", "exchange", "seas_stor", "description", "data_id" FROM src."Technology";

INSERT INTO "technology_label" ("tech", "notes")
SELECT "tech", "notes" FROM src."TechnologyLabel";

INSERT OR IGNORE INTO "technology_type" ("label", "description")
SELECT "label", "description" FROM src."TechnologyType";

INSERT INTO "time_period" ("sequence", "period", "flag")
SELECT "sequence", "period", "flag" FROM src."TimePeriod";

INSERT OR IGNORE INTO "time_period_type" ("label", "description")
SELECT "label", "description" FROM src."TimePeriodType";
