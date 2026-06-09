from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..base import CanoeBaseModel

from .enums import (
    CommodityTypeCode,
    OperatorCode,
    TechnologyTypeCode,
    TimePeriodTypeCode,
    DataQualityCredibilityLevel,
    DataQualityGeographyLevel,
    DataQualityStructureLevel,
    DataQualityTechnologyLevel,
    DataQualityTimeLevel,
)


# ===========================================================
# Metadata
# ===========================================================

class Metadata(CanoeBaseModel):
    """Pydantic model for SQL table `metadata`."""
    __table_name__: ClassVar[str] = 'metadata'
    __primary_key__: ClassVar[tuple[str, ...]] = ('element',)
    element: str = ...
    value: int | None = None
    notes: str | None = None


class MetadataReal(CanoeBaseModel):
    """Pydantic model for SQL table `metadata_real`."""
    __table_name__: ClassVar[str] = 'metadata_real'
    __primary_key__: ClassVar[tuple[str, ...]] = ('element',)
    element: str = ...
    value: float | None = None
    notes: str | None = None


# ===========================================================
# Label / registry tables
# ===========================================================

class CommodityLabel(CanoeBaseModel):
    """Pydantic model for SQL table `commodity_label`."""
    __table_name__: ClassVar[str] = 'commodity_label'
    __primary_key__: ClassVar[tuple[str, ...]] = ('commodity',)
    commodity: str = ...
    notes: str | None = None


class TechnologyLabel(CanoeBaseModel):
    """Pydantic model for SQL table `technology_label`."""
    __table_name__: ClassVar[str] = 'technology_label'
    __primary_key__: ClassVar[tuple[str, ...]] = ('tech',)
    tech: str = ...
    notes: str | None = None


class TechGroupLabel(CanoeBaseModel):
    """Pydantic model for SQL table `tech_group_label`."""
    __table_name__: ClassVar[str] = 'tech_group_label'
    __primary_key__: ClassVar[tuple[str, ...]] = ('group_name',)
    group_name: str = ...
    notes: str | None = None


class SectorLabel(CanoeBaseModel):
    """Pydantic model for SQL table `sector_label`."""
    __table_name__: ClassVar[str] = 'sector_label'
    __primary_key__: ClassVar[tuple[str, ...]] = ('sector',)
    sector: str = ...
    notes: str | None = None


# ===========================================================
# Enum / type tables
# ===========================================================

class CommodityType(CanoeBaseModel):
    """Pydantic model for SQL table `commodity_type`."""
    __table_name__: ClassVar[str] = 'commodity_type'
    __primary_key__: ClassVar[tuple[str, ...]] = ('label',)
    label: str = ...
    description: str | None = None


class TechnologyType(CanoeBaseModel):
    """Pydantic model for SQL table `technology_type`."""
    __table_name__: ClassVar[str] = 'technology_type'
    __primary_key__: ClassVar[tuple[str, ...]] = ('label',)
    label: str = ...
    description: str | None = None


class TimePeriodType(CanoeBaseModel):
    """Pydantic model for SQL table `time_period_type`."""
    __table_name__: ClassVar[str] = 'time_period_type'
    __primary_key__: ClassVar[tuple[str, ...]] = ('label',)
    label: str = ...
    description: str | None = None


class Operator(CanoeBaseModel):
    """Pydantic model for SQL table `operator`."""
    __table_name__: ClassVar[str] = 'operator'
    __primary_key__: ClassVar[tuple[str, ...]] = ('operator',)
    operator: OperatorCode = ...
    notes: str | None = None


# ===========================================================
# Data quality and data source tables
# ===========================================================

class DataQualityCredibility(CanoeBaseModel):
    """Pydantic model for SQL table `data_quality_credibility`."""
    __table_name__: ClassVar[str] = 'data_quality_credibility'
    __primary_key__: ClassVar[tuple[str, ...]] = ('dq_cred',)
    dq_cred: DataQualityCredibilityLevel = ...
    description: str | None = None


class DataQualityGeography(CanoeBaseModel):
    """Pydantic model for SQL table `data_quality_geography`."""
    __table_name__: ClassVar[str] = 'data_quality_geography'
    __primary_key__: ClassVar[tuple[str, ...]] = ('dq_geog',)
    dq_geog: DataQualityGeographyLevel = ...
    description: str | None = None


class DataQualityStructure(CanoeBaseModel):
    """Pydantic model for SQL table `data_quality_structure`."""
    __table_name__: ClassVar[str] = 'data_quality_structure'
    __primary_key__: ClassVar[tuple[str, ...]] = ('dq_struc',)
    dq_struc: DataQualityStructureLevel = ...
    description: str | None = None


class DataQualityTechnology(CanoeBaseModel):
    """Pydantic model for SQL table `data_quality_technology`."""
    __table_name__: ClassVar[str] = 'data_quality_technology'
    __primary_key__: ClassVar[tuple[str, ...]] = ('dq_tech',)
    dq_tech: DataQualityTechnologyLevel = ...
    description: str | None = None


class DataQualityTime(CanoeBaseModel):
    """Pydantic model for SQL table `data_quality_time`."""
    __table_name__: ClassVar[str] = 'data_quality_time'
    __primary_key__: ClassVar[tuple[str, ...]] = ('dq_time',)
    dq_time: DataQualityTimeLevel = ...
    description: str | None = None


class DataSourceLabel(CanoeBaseModel):
    """Pydantic model for SQL table `data_source_label`."""
    __table_name__: ClassVar[str] = 'data_source_label'
    __primary_key__: ClassVar[tuple[str, ...]] = ('source_id',)
    source_id: str = ...
    notes: str | None = None


class DataSet(CanoeBaseModel):
    """Pydantic model for SQL table `data_set`."""
    __table_name__: ClassVar[str] = 'data_set'
    __primary_key__: ClassVar[tuple[str, ...]] = ('data_id',)
    data_id: str = ...
    label: str | None = None
    version: str | None = None
    description: str | None = None
    status: str | None = None
    author: str | None = None
    date: str | None = None
    parent_id: str | None = None
    changelog: str | None = None
    notes: str | None = None


class DataSource(CanoeBaseModel):
    """Pydantic model for SQL table `data_source`."""
    __table_name__: ClassVar[str] = 'data_source'
    __primary_key__: ClassVar[tuple[str, ...]] = ('source_id', 'data_id')
    source_id: str = ...
    source: str | None = None
    notes: str | None = None
    data_id: str = ...


# ===========================================================
# Time tables
# ===========================================================

class TimePeriod(CanoeBaseModel):
    """Pydantic model for SQL table `time_period`."""
    __table_name__: ClassVar[str] = 'time_period'
    __primary_key__: ClassVar[tuple[str, ...]] = ('period',)
    sequence: int | None = None
    period: int = ...
    flag: TimePeriodTypeCode | None = None


class TimeOfDay(CanoeBaseModel):
    """Pydantic model for SQL table `time_of_day`.

    `hours` represents the number of hours in this time-of-day slice.
    Defaults to 1 if not specified; must be > 0.
    """
    __table_name__: ClassVar[str] = 'time_of_day'
    __primary_key__: ClassVar[tuple[str, ...]] = ('tod',)
    sequence: int | None = None
    tod: str = ...
    hours: float = Field(1.0, gt=0)
    notes: str | None = None


class TimeSeason(CanoeBaseModel):
    """Pydantic model for SQL table `time_season`.

    Replaces the 3.2 SeasonLabel / TimeSeason / TimeSegmentFraction trio.
    `segment_fraction` is the global fraction of the year this season represents.
    """
    __table_name__: ClassVar[str] = 'time_season'
    __primary_key__: ClassVar[tuple[str, ...]] = ('season',)
    sequence: int | None = None
    season: str = ...
    segment_fraction: float = Field(..., ge=0, le=1)
    notes: str | None = None


class TimeSeasonSequential(CanoeBaseModel):
    """Pydantic model for SQL table `time_season_sequential`.

    Replaces the 3.2 TimeSeasonSequential. Now period-independent:
    `seas_seq` is the unique season-slice identifier; `segment_fraction`
    replaces the old per-period `num_days` field.
    """
    __table_name__: ClassVar[str] = 'time_season_sequential'
    __primary_key__: ClassVar[tuple[str, ...]] = ('seas_seq',)
    sequence: int | None = None
    seas_seq: str = ...
    season: str | None = None
    segment_fraction: float = Field(..., ge=0, le=1)
    notes: str | None = None


# ===========================================================
# Region
# ===========================================================

class Region(CanoeBaseModel):
    """Pydantic model for SQL table `region`."""
    __table_name__: ClassVar[str] = 'region'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region',)
    region: str = ...
    notes: str | None = None


# ===========================================================
# Core model definition tables
# ===========================================================

class Commodity(CanoeBaseModel):
    """Pydantic model for SQL table `commodity`."""
    __table_name__: ClassVar[str] = 'commodity'
    __primary_key__: ClassVar[tuple[str, ...]] = ('name', 'data_id')
    name: str = ...
    flag: CommodityTypeCode | None = None
    description: str | None = None
    units: str | None = None
    data_id: str = ...


class Technology(CanoeBaseModel):
    """Pydantic model for SQL table `technology`."""
    __table_name__: ClassVar[str] = 'technology'
    __primary_key__: ClassVar[tuple[str, ...]] = ('tech', 'data_id')
    tech: str = ...
    flag: TechnologyTypeCode = ...
    sector: str | None = None
    category: str | None = None
    sub_category: str | None = None
    unlim_cap: int = 0
    annual: int = 0
    reserve: int = 0
    curtail: int = 0
    retire: int = 0
    flex: int = 0
    exchange: int = 0
    seas_stor: int = 0
    description: str | None = None
    data_id: str = ...


class TechGroup(CanoeBaseModel):
    """Pydantic model for SQL table `tech_group`."""
    __table_name__: ClassVar[str] = 'tech_group'
    __primary_key__: ClassVar[tuple[str, ...]] = ('group_name', 'data_id')
    group_name: str = ...
    notes: str | None = None
    data_id: str = ...


class TechGroupMember(CanoeBaseModel):
    """Pydantic model for SQL table `tech_group_member`."""
    __table_name__: ClassVar[str] = 'tech_group_member'
    __primary_key__: ClassVar[tuple[str, ...]] = ('group_name', 'tech', 'data_id')
    group_name: str = ...
    tech: str = ...
    data_id: str = ...


# ===========================================================
# Data tables
# All include: data_id (in PK), data_source, dq_cred/geog/struc/tech/time
# ===========================================================

class CapacityCredit(CanoeBaseModel):
    """Pydantic model for SQL table `capacity_credit`."""
    __table_name__: ClassVar[str] = 'capacity_credit'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'tech', 'vintage', 'data_id')
    region: str = ...
    period: int = ...
    tech: str = ...
    vintage: int = ...
    credit: float | None = Field(None, ge=0, le=1)
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class CapacityFactorProcess(CanoeBaseModel):
    """Pydantic model for SQL table `capacity_factor_process`.

    Note: `period` has been removed vs 3.2; capacity factors are now
    season-global rather than per-period.
    """
    __table_name__: ClassVar[str] = 'capacity_factor_process'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'season', 'tod', 'tech', 'vintage', 'data_id')
    region: str = ...
    season: str = ...
    tod: str = ...
    tech: str = ...
    vintage: int = ...
    factor: float | None = Field(None, ge=0, le=1)
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class CapacityFactorTech(CanoeBaseModel):
    """Pydantic model for SQL table `capacity_factor_tech`.

    Note: `period` has been removed vs 3.2.
    """
    __table_name__: ClassVar[str] = 'capacity_factor_tech'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'season', 'tod', 'tech', 'data_id')
    region: str = ...
    season: str = ...
    tod: str = ...
    tech: str = ...
    factor: float | None = Field(None, ge=0, le=1)
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class CapacityToActivity(CanoeBaseModel):
    """Pydantic model for SQL table `capacity_to_activity`."""
    __table_name__: ClassVar[str] = 'capacity_to_activity'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech', 'data_id')
    region: str = ...
    tech: str = ...
    c2a: float | None = None
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class ConstructionInput(CanoeBaseModel):
    """Pydantic model for SQL table `construction_input`."""
    __table_name__: ClassVar[str] = 'construction_input'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'input_comm', 'tech', 'vintage', 'data_id')
    region: str = ...
    input_comm: str = ...
    tech: str = ...
    vintage: int = ...
    value: float | None = None
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class CostEmission(CanoeBaseModel):
    """Pydantic model for SQL table `cost_emission`."""
    __table_name__: ClassVar[str] = 'cost_emission'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'emis_comm', 'data_id')
    region: str = ...
    period: int = ...
    emis_comm: str = ...
    cost: float = ...
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class CostFixed(CanoeBaseModel):
    """Pydantic model for SQL table `cost_fixed`."""
    __table_name__: ClassVar[str] = 'cost_fixed'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'tech', 'vintage', 'data_id')
    region: str = ...
    period: int = ...
    tech: str = ...
    vintage: int = ...
    cost: float | None = None
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class CostInvest(CanoeBaseModel):
    """Pydantic model for SQL table `cost_invest`."""
    __table_name__: ClassVar[str] = 'cost_invest'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech', 'vintage', 'data_id')
    region: str = ...
    tech: str = ...
    vintage: int = ...
    cost: float | None = None
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class CostVariable(CanoeBaseModel):
    """Pydantic model for SQL table `cost_variable`."""
    __table_name__: ClassVar[str] = 'cost_variable'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'tech', 'vintage', 'data_id')
    region: str = ...
    period: int = ...
    tech: str = ...
    vintage: int = ...
    cost: float | None = None
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class Demand(CanoeBaseModel):
    """Pydantic model for SQL table `demand`."""
    __table_name__: ClassVar[str] = 'demand'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'commodity', 'data_id')
    region: str = ...
    period: int = ...
    commodity: str = ...
    demand: float | None = None
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class DemandSpecificDistribution(CanoeBaseModel):
    """Pydantic model for SQL table `demand_specific_distribution`."""
    __table_name__: ClassVar[str] = 'demand_specific_distribution'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'season', 'tod', 'demand_name', 'data_id')
    region: str = ...
    period: int = ...
    season: str = ...
    tod: str = ...
    demand_name: str = ...
    dsd: float | None = Field(None, ge=0, le=1)
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class EndOfLifeOutput(CanoeBaseModel):
    """Pydantic model for SQL table `end_of_life_output`."""
    __table_name__: ClassVar[str] = 'end_of_life_output'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech', 'vintage', 'output_comm', 'data_id')
    region: str = ...
    tech: str = ...
    vintage: int = ...
    output_comm: str = ...
    value: float | None = None
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class Efficiency(CanoeBaseModel):
    """Pydantic model for SQL table `efficiency`."""
    __table_name__: ClassVar[str] = 'efficiency'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'input_comm', 'tech', 'vintage', 'output_comm', 'data_id')
    region: str = ...
    input_comm: str = ...
    tech: str = ...
    vintage: int = ...
    output_comm: str = ...
    efficiency: float | None = Field(None, gt=0)
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class EfficiencyVariable(CanoeBaseModel):
    """Pydantic model for SQL table `efficiency_variable`.

    Note: `period` has been removed vs 3.2; efficiency is now
    season-global rather than per-period.
    """
    __table_name__: ClassVar[str] = 'efficiency_variable'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'season', 'tod', 'input_comm', 'tech', 'vintage', 'output_comm', 'data_id')
    region: str = ...
    season: str = ...
    tod: str = ...
    input_comm: str = ...
    tech: str = ...
    vintage: int = ...
    output_comm: str = ...
    efficiency: float | None = Field(None, gt=0)
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class EmissionActivity(CanoeBaseModel):
    """Pydantic model for SQL table `emission_activity`."""
    __table_name__: ClassVar[str] = 'emission_activity'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'emis_comm', 'input_comm', 'tech', 'vintage', 'output_comm', 'data_id')
    region: str = ...
    emis_comm: str = ...
    input_comm: str = ...
    tech: str = ...
    vintage: int = ...
    output_comm: str = ...
    activity: float | None = None
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class EmissionEmbodied(CanoeBaseModel):
    """Pydantic model for SQL table `emission_embodied`."""
    __table_name__: ClassVar[str] = 'emission_embodied'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'emis_comm', 'tech', 'vintage', 'data_id')
    region: str = ...
    emis_comm: str = ...
    tech: str = ...
    vintage: int = ...
    value: float | None = None
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class EmissionEndOfLife(CanoeBaseModel):
    """Pydantic model for SQL table `emission_end_of_life`."""
    __table_name__: ClassVar[str] = 'emission_end_of_life'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'emis_comm', 'tech', 'vintage', 'data_id')
    region: str = ...
    emis_comm: str = ...
    tech: str = ...
    vintage: int = ...
    value: float | None = None
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class ExistingCapacity(CanoeBaseModel):
    """Pydantic model for SQL table `existing_capacity`."""
    __table_name__: ClassVar[str] = 'existing_capacity'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech', 'vintage', 'data_id')
    region: str = ...
    tech: str = ...
    vintage: int = ...
    capacity: float | None = None
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LoanLifetimeProcess(CanoeBaseModel):
    """Pydantic model for SQL table `loan_lifetime_process`."""
    __table_name__: ClassVar[str] = 'loan_lifetime_process'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech', 'vintage', 'data_id')
    region: str = ...
    tech: str = ...
    vintage: int = ...
    lifetime: float | None = None
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LoanRate(CanoeBaseModel):
    """Pydantic model for SQL table `loan_rate`."""
    __table_name__: ClassVar[str] = 'loan_rate'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech', 'vintage', 'data_id')
    region: str = ...
    tech: str = ...
    vintage: int = ...
    rate: float | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LifetimeProcess(CanoeBaseModel):
    """Pydantic model for SQL table `lifetime_process`."""
    __table_name__: ClassVar[str] = 'lifetime_process'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech', 'vintage', 'data_id')
    region: str = ...
    tech: str = ...
    vintage: int = ...
    lifetime: float | None = None
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LifetimeTech(CanoeBaseModel):
    """Pydantic model for SQL table `lifetime_tech`."""
    __table_name__: ClassVar[str] = 'lifetime_tech'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech', 'data_id')
    region: str = ...
    tech: str = ...
    lifetime: float | None = None
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


# ===========================================================
# Limit / constraint tables
# ===========================================================

class LimitGrowthCapacity(CanoeBaseModel):
    """Pydantic model for SQL table `limit_growth_capacity`."""
    __table_name__: ClassVar[str] = 'limit_growth_capacity'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech_or_group', 'operator', 'data_id')
    region: str = ...
    tech_or_group: str = ...
    operator: OperatorCode = OperatorCode.LE
    rate: float = 0
    seed: float = 0
    seed_units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitDegrowthCapacity(CanoeBaseModel):
    """Pydantic model for SQL table `limit_degrowth_capacity`."""
    __table_name__: ClassVar[str] = 'limit_degrowth_capacity'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech_or_group', 'operator', 'data_id')
    region: str = ...
    tech_or_group: str = ...
    operator: OperatorCode = OperatorCode.LE
    rate: float = 0
    seed: float = 0
    seed_units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitGrowthNewCapacity(CanoeBaseModel):
    """Pydantic model for SQL table `limit_growth_new_capacity`."""
    __table_name__: ClassVar[str] = 'limit_growth_new_capacity'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech_or_group', 'operator', 'data_id')
    region: str = ...
    tech_or_group: str = ...
    operator: OperatorCode = OperatorCode.LE
    rate: float = 0
    seed: float = 0
    seed_units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitDegrowthNewCapacity(CanoeBaseModel):
    """Pydantic model for SQL table `limit_degrowth_new_capacity`."""
    __table_name__: ClassVar[str] = 'limit_degrowth_new_capacity'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech_or_group', 'operator', 'data_id')
    region: str = ...
    tech_or_group: str = ...
    operator: OperatorCode = OperatorCode.LE
    rate: float = 0
    seed: float = 0
    seed_units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitGrowthNewCapacityDelta(CanoeBaseModel):
    """Pydantic model for SQL table `limit_growth_new_capacity_delta`."""
    __table_name__: ClassVar[str] = 'limit_growth_new_capacity_delta'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech_or_group', 'operator', 'data_id')
    region: str = ...
    tech_or_group: str = ...
    operator: OperatorCode = OperatorCode.LE
    rate: float = 0
    seed: float = 0
    seed_units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitDegrowthNewCapacityDelta(CanoeBaseModel):
    """Pydantic model for SQL table `limit_degrowth_new_capacity_delta`."""
    __table_name__: ClassVar[str] = 'limit_degrowth_new_capacity_delta'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech_or_group', 'operator', 'data_id')
    region: str = ...
    tech_or_group: str = ...
    operator: OperatorCode = OperatorCode.LE
    rate: float = 0
    seed: float = 0
    seed_units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitStorageLevelFraction(CanoeBaseModel):
    """Pydantic model for SQL table `limit_storage_level_fraction`.

    Note: `period` and `vintage` have been removed vs 3.2.
    """
    __table_name__: ClassVar[str] = 'limit_storage_level_fraction'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'season', 'tod', 'tech', 'operator', 'data_id')
    region: str = ...
    season: str = ...
    tod: str = ...
    tech: str = ...
    operator: OperatorCode = OperatorCode.LE
    fraction: float | None = Field(None, ge=0, le=1)
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitActivity(CanoeBaseModel):
    """Pydantic model for SQL table `limit_activity`."""
    __table_name__: ClassVar[str] = 'limit_activity'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'tech_or_group', 'operator', 'data_id')
    region: str = ...
    period: int = ...
    tech_or_group: str = ...
    operator: OperatorCode = OperatorCode.LE
    activity: float | None = None
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitActivityShare(CanoeBaseModel):
    """Pydantic model for SQL table `limit_activity_share`."""
    __table_name__: ClassVar[str] = 'limit_activity_share'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'sub_group', 'super_group', 'operator', 'data_id')
    region: str = ...
    period: int = ...
    sub_group: str = ...
    super_group: str = ...
    operator: OperatorCode = OperatorCode.LE
    share: float | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitAnnualCapacityFactor(CanoeBaseModel):
    """Pydantic model for SQL table `limit_annual_capacity_factor`.

    Note: `tech` has been widened to `tech_or_group` vs 3.2.
    """
    __table_name__: ClassVar[str] = 'limit_annual_capacity_factor'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech_or_group', 'vintage', 'output_comm', 'operator', 'data_id')
    region: str = ...
    tech_or_group: str = ...
    vintage: int = ...
    output_comm: str = ...
    operator: OperatorCode = OperatorCode.LE
    factor: float | None = Field(None, ge=0, le=1)
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitCapacity(CanoeBaseModel):
    """Pydantic model for SQL table `limit_capacity`."""
    __table_name__: ClassVar[str] = 'limit_capacity'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'tech_or_group', 'operator', 'data_id')
    region: str = ...
    period: int = ...
    tech_or_group: str = ...
    operator: OperatorCode = OperatorCode.LE
    capacity: float | None = None
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitCapacityShare(CanoeBaseModel):
    """Pydantic model for SQL table `limit_capacity_share`."""
    __table_name__: ClassVar[str] = 'limit_capacity_share'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'sub_group', 'super_group', 'operator', 'data_id')
    region: str = ...
    period: int = ...
    sub_group: str = ...
    super_group: str = ...
    operator: OperatorCode = OperatorCode.LE
    share: float | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitNewCapacity(CanoeBaseModel):
    """Pydantic model for SQL table `limit_new_capacity`.

    Note: `period` has been replaced by `vintage` vs 3.2. The constraint
    now applies per vintage rather than per model period.
    """
    __table_name__: ClassVar[str] = 'limit_new_capacity'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech_or_group', 'vintage', 'operator', 'data_id')
    region: str = ...
    tech_or_group: str = ...
    vintage: int = ...
    operator: OperatorCode = OperatorCode.LE
    new_cap: float | None = None
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitNewCapacityShare(CanoeBaseModel):
    """Pydantic model for SQL table `limit_new_capacity_share`.

    Note: `period` has been replaced by `vintage` vs 3.2.
    """
    __table_name__: ClassVar[str] = 'limit_new_capacity_share'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'sub_group', 'super_group', 'vintage', 'operator', 'data_id')
    region: str = ...
    sub_group: str = ...
    super_group: str = ...
    vintage: int = ...
    operator: OperatorCode = OperatorCode.LE
    share: float | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitResource(CanoeBaseModel):
    """Pydantic model for SQL table `limit_resource`."""
    __table_name__: ClassVar[str] = 'limit_resource'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech_or_group', 'operator', 'data_id')
    region: str = ...
    tech_or_group: str = ...
    operator: OperatorCode = OperatorCode.LE
    cum_act: float | None = None
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitSeasonalCapacityFactor(CanoeBaseModel):
    """Pydantic model for SQL table `limit_seasonal_capacity_factor`.

    Note: `period` has been removed and `tech` widened to `tech_or_group` vs 3.2.
    """
    __table_name__: ClassVar[str] = 'limit_seasonal_capacity_factor'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'season', 'tech_or_group', 'operator', 'data_id')
    region: str = ...
    season: str = ...
    tech_or_group: str = ...
    operator: OperatorCode = OperatorCode.LE
    factor: float | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitTechInputSplit(CanoeBaseModel):
    """Pydantic model for SQL table `limit_tech_input_split`."""
    __table_name__: ClassVar[str] = 'limit_tech_input_split'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'input_comm', 'tech', 'operator', 'data_id')
    region: str = ...
    period: int = ...
    input_comm: str = ...
    tech: str = ...
    operator: OperatorCode = OperatorCode.LE
    proportion: float | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitTechInputSplitAnnual(CanoeBaseModel):
    """Pydantic model for SQL table `limit_tech_input_split_annual`."""
    __table_name__: ClassVar[str] = 'limit_tech_input_split_annual'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'input_comm', 'tech', 'operator', 'data_id')
    region: str = ...
    period: int = ...
    input_comm: str = ...
    tech: str = ...
    operator: OperatorCode = OperatorCode.LE
    proportion: float | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitTechOutputSplit(CanoeBaseModel):
    """Pydantic model for SQL table `limit_tech_output_split`."""
    __table_name__: ClassVar[str] = 'limit_tech_output_split'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'tech', 'output_comm', 'operator', 'data_id')
    region: str = ...
    period: int = ...
    tech: str = ...
    output_comm: str = ...
    operator: OperatorCode = OperatorCode.LE
    proportion: float | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitTechOutputSplitAnnual(CanoeBaseModel):
    """Pydantic model for SQL table `limit_tech_output_split_annual`."""
    __table_name__: ClassVar[str] = 'limit_tech_output_split_annual'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'tech', 'output_comm', 'operator', 'data_id')
    region: str = ...
    period: int = ...
    tech: str = ...
    output_comm: str = ...
    operator: OperatorCode = OperatorCode.LE
    proportion: float | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitEmission(CanoeBaseModel):
    """Pydantic model for SQL table `limit_emission`."""
    __table_name__: ClassVar[str] = 'limit_emission'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'emis_comm', 'operator', 'data_id')
    region: str = ...
    period: int = ...
    emis_comm: str = ...
    operator: OperatorCode = OperatorCode.LE
    value: float | None = None
    units: str | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LinkedTech(CanoeBaseModel):
    """Pydantic model for SQL table `linked_tech`."""
    __table_name__: ClassVar[str] = 'linked_tech'
    __primary_key__: ClassVar[tuple[str, ...]] = ('primary_region', 'primary_tech', 'emis_comm', 'data_id')
    primary_region: str = ...
    primary_tech: str = ...
    emis_comm: str = ...
    driven_tech: str | None = None
    notes: str | None = None
    data_source: str | None = None
    data_id: str = ...


class PlanningReserveMargin(CanoeBaseModel):
    """Pydantic model for SQL table `planning_reserve_margin`."""
    __table_name__: ClassVar[str] = 'planning_reserve_margin'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'data_id')
    region: str = ...
    margin: float | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class RampDownHourly(CanoeBaseModel):
    """Pydantic model for SQL table `ramp_down_hourly`."""
    __table_name__: ClassVar[str] = 'ramp_down_hourly'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech', 'data_id')
    region: str = ...
    tech: str = ...
    rate: float | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class RampUpHourly(CanoeBaseModel):
    """Pydantic model for SQL table `ramp_up_hourly`."""
    __table_name__: ClassVar[str] = 'ramp_up_hourly'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech', 'data_id')
    region: str = ...
    tech: str = ...
    rate: float | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class ReserveCapacityDerate(CanoeBaseModel):
    """Pydantic model for SQL table `reserve_capacity_derate`.

    Note: `period` has been removed vs 3.2.
    """
    __table_name__: ClassVar[str] = 'reserve_capacity_derate'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'season', 'tech', 'vintage', 'data_id')
    region: str = ...
    season: str = ...
    tech: str = ...
    vintage: int = ...
    factor: float | None = Field(None, ge=0, le=1)
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class StorageDuration(CanoeBaseModel):
    """Pydantic model for SQL table `storage_duration`."""
    __table_name__: ClassVar[str] = 'storage_duration'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech', 'data_id')
    region: str = ...
    tech: str = ...
    duration: float | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LifetimeSurvivalCurve(CanoeBaseModel):
    """Pydantic model for SQL table `lifetime_survival_curve`."""
    __table_name__: ClassVar[str] = 'lifetime_survival_curve'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'tech', 'vintage', 'data_id')
    region: str = ...
    period: int = ...
    tech: str = ...
    vintage: int = ...
    fraction: float | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class RPSRequirement(CanoeBaseModel):
    """Pydantic model for SQL table `rps_requirement`.

    Note: PK expanded vs 3.2 from (region, data_id) to
    (region, period, tech_group, data_id), allowing multiple RPS entries
    per region per dataset.
    """
    __table_name__: ClassVar[str] = 'rps_requirement'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'tech_group', 'data_id')
    region: str = ...
    period: int = ...
    tech_group: str = ...
    requirement: float = ...
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


__all__ = [
    'Metadata', 'MetadataReal',
    # Label / registry
    'CommodityLabel', 'TechnologyLabel', 'TechGroupLabel', 'SectorLabel',
    # Enum / type
    'CommodityType', 'TechnologyType', 'TimePeriodType', 'Operator',
    # Data quality & provenance
    'DataQualityCredibility', 'DataQualityGeography', 'DataQualityStructure',
    'DataQualityTechnology', 'DataQualityTime',
    'DataSourceLabel', 'DataSet', 'DataSource',
    # Time
    'TimePeriod', 'TimeOfDay', 'TimeSeason', 'TimeSeasonSequential',
    # Region
    'Region',
    # Core model
    'Commodity', 'Technology', 'TechGroup', 'TechGroupMember',
    # Data tables
    'CapacityCredit', 'CapacityFactorProcess', 'CapacityFactorTech',
    'CapacityToActivity', 'ConstructionInput',
    'CostEmission', 'CostFixed', 'CostInvest', 'CostVariable',
    'Demand', 'DemandSpecificDistribution',
    'EndOfLifeOutput', 'Efficiency', 'EfficiencyVariable',
    'EmissionActivity', 'EmissionEmbodied', 'EmissionEndOfLife',
    'ExistingCapacity',
    'LoanLifetimeProcess', 'LoanRate', 'LifetimeProcess', 'LifetimeTech',
    'LifetimeSurvivalCurve',
    # Limit / constraint tables
    'LimitGrowthCapacity', 'LimitDegrowthCapacity',
    'LimitGrowthNewCapacity', 'LimitDegrowthNewCapacity',
    'LimitGrowthNewCapacityDelta', 'LimitDegrowthNewCapacityDelta',
    'LimitStorageLevelFraction',
    'LimitActivity', 'LimitActivityShare',
    'LimitAnnualCapacityFactor',
    'LimitCapacity', 'LimitCapacityShare',
    'LimitNewCapacity', 'LimitNewCapacityShare',
    'LimitResource', 'LimitSeasonalCapacityFactor',
    'LimitTechInputSplit', 'LimitTechInputSplitAnnual',
    'LimitTechOutputSplit', 'LimitTechOutputSplitAnnual',
    'LimitEmission',
    'LinkedTech', 'PlanningReserveMargin',
    'RampDownHourly', 'RampUpHourly',
    'ReserveCapacityDerate', 'StorageDuration',
    'RPSRequirement',
]
