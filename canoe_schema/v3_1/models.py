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


class MetaData(CanoeBaseModel):
    """Pydantic model for SQL table `MetaData`."""
    __table_name__: ClassVar[str] = 'MetaData'
    __primary_key__: ClassVar[tuple[str, ...]] = ('element',)
    element: str = ...
    value: int | None = None
    notes: str | None = None


class MetaDataReal(CanoeBaseModel):
    """Pydantic model for SQL table `MetaDataReal`."""
    __table_name__: ClassVar[str] = 'MetaDataReal'
    __primary_key__: ClassVar[tuple[str, ...]] = ('element',)
    element: str = ...
    value: float | None = None
    notes: str | None = None


class SeasonLabel(CanoeBaseModel):
    """Pydantic model for SQL table `SeasonLabel`."""
    __table_name__: ClassVar[str] = 'SeasonLabel'
    __primary_key__: ClassVar[tuple[str, ...]] = ('season',)
    season: str = ...
    notes: str | None = None


class SectorLabel(CanoeBaseModel):
    """Pydantic model for SQL table `SectorLabel`."""
    __table_name__: ClassVar[str] = 'SectorLabel'
    __primary_key__: ClassVar[tuple[str, ...]] = ('sector',)
    sector: str = ...
    notes: str | None = None


class CapacityCredit(CanoeBaseModel):
    """Pydantic model for SQL table `CapacityCredit`."""
    __table_name__: ClassVar[str] = 'CapacityCredit'
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
    """Pydantic model for SQL table `CapacityFactorProcess`."""
    __table_name__: ClassVar[str] = 'CapacityFactorProcess'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'season', 'tod', 'tech', 'vintage', 'data_id')
    region: str = ...
    period: int = ...
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
    """Pydantic model for SQL table `CapacityFactorTech`."""
    __table_name__: ClassVar[str] = 'CapacityFactorTech'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'season', 'tod', 'tech', 'data_id')
    region: str = ...
    period: int = ...
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
    """Pydantic model for SQL table `CapacityToActivity`."""
    __table_name__: ClassVar[str] = 'CapacityToActivity'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech', 'data_id')
    region: str = ...
    tech: str = ...
    c2a: float | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class Commodity(CanoeBaseModel):
    """Pydantic model for SQL table `Commodity`."""
    __table_name__: ClassVar[str] = 'Commodity'
    __primary_key__: ClassVar[tuple[str, ...]] = ('name', 'data_id')
    name: str = ...
    flag: CommodityTypeCode | None = None
    description: str | None = None
    data_id: str = ...


class CommodityType(CanoeBaseModel):
    """Pydantic model for SQL table `CommodityType`."""
    __table_name__: ClassVar[str] = 'CommodityType'
    __primary_key__: ClassVar[tuple[str, ...]] = ('label',)
    label: str = ...
    description: str | None = None


class ConstructionInput(CanoeBaseModel):
    """Pydantic model for SQL table `ConstructionInput`."""
    __table_name__: ClassVar[str] = 'ConstructionInput'
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
    """Pydantic model for SQL table `CostEmission`."""
    __table_name__: ClassVar[str] = 'CostEmission'
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
    """Pydantic model for SQL table `CostFixed`."""
    __table_name__: ClassVar[str] = 'CostFixed'
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
    """Pydantic model for SQL table `CostInvest`."""
    __table_name__: ClassVar[str] = 'CostInvest'
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
    """Pydantic model for SQL table `CostVariable`."""
    __table_name__: ClassVar[str] = 'CostVariable'
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
    """Pydantic model for SQL table `Demand`."""
    __table_name__: ClassVar[str] = 'Demand'
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
    """Pydantic model for SQL table `DemandSpecificDistribution`."""
    __table_name__: ClassVar[str] = 'DemandSpecificDistribution'
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
    """Pydantic model for SQL table `EndOfLifeOutput`."""
    __table_name__: ClassVar[str] = 'EndOfLifeOutput'
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
    """Pydantic model for SQL table `Efficiency`."""
    __table_name__: ClassVar[str] = 'Efficiency'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'input_comm', 'tech', 'vintage', 'output_comm', 'data_id')
    region: str = ...
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


class EfficiencyVariable(CanoeBaseModel):
    """Pydantic model for SQL table `EfficiencyVariable`."""
    __table_name__: ClassVar[str] = 'EfficiencyVariable'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'season', 'tod', 'input_comm', 'tech', 'vintage', 'output_comm', 'data_id')
    region: str = ...
    period: int = ...
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
    """Pydantic model for SQL table `EmissionActivity`."""
    __table_name__: ClassVar[str] = 'EmissionActivity'
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
    """Pydantic model for SQL table `EmissionEmbodied`."""
    __table_name__: ClassVar[str] = 'EmissionEmbodied'
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
    """Pydantic model for SQL table `EmissionEndOfLife`."""
    __table_name__: ClassVar[str] = 'EmissionEndOfLife'
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
    """Pydantic model for SQL table `ExistingCapacity`."""
    __table_name__: ClassVar[str] = 'ExistingCapacity'
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


class TechGroup(CanoeBaseModel):
    """Pydantic model for SQL table `TechGroup`."""
    __table_name__: ClassVar[str] = 'TechGroup'
    __primary_key__: ClassVar[tuple[str, ...]] = ('group_name', 'data_id')
    group_name: str = ...
    notes: str | None = None
    data_id: str = ...


class LoanLifetimeProcess(CanoeBaseModel):
    """Pydantic model for SQL table `LoanLifetimeProcess`."""
    __table_name__: ClassVar[str] = 'LoanLifetimeProcess'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech', 'vintage', 'data_id')
    region: str = ...
    tech: str = ...
    vintage: int = ...
    lifetime: float | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LoanRate(CanoeBaseModel):
    """Pydantic model for SQL table `LoanRate`."""
    __table_name__: ClassVar[str] = 'LoanRate'
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
    """Pydantic model for SQL table `LifetimeProcess`."""
    __table_name__: ClassVar[str] = 'LifetimeProcess'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech', 'vintage', 'data_id')
    region: str = ...
    tech: str = ...
    vintage: int = ...
    lifetime: float | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LifetimeTech(CanoeBaseModel):
    """Pydantic model for SQL table `LifetimeTech`."""
    __table_name__: ClassVar[str] = 'LifetimeTech'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'tech', 'data_id')
    region: str = ...
    tech: str = ...
    lifetime: float | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class Operator(CanoeBaseModel):
    """Pydantic model for SQL table `Operator`."""
    __table_name__: ClassVar[str] = 'Operator'
    __primary_key__: ClassVar[tuple[str, ...]] = ('operator',)
    operator: OperatorCode = ...
    notes: str | None = None


class LimitGrowthCapacity(CanoeBaseModel):
    """Pydantic model for SQL table `LimitGrowthCapacity`."""
    __table_name__: ClassVar[str] = 'LimitGrowthCapacity'
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
    """Pydantic model for SQL table `LimitDegrowthCapacity`."""
    __table_name__: ClassVar[str] = 'LimitDegrowthCapacity'
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
    """Pydantic model for SQL table `LimitGrowthNewCapacity`."""
    __table_name__: ClassVar[str] = 'LimitGrowthNewCapacity'
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
    """Pydantic model for SQL table `LimitDegrowthNewCapacity`."""
    __table_name__: ClassVar[str] = 'LimitDegrowthNewCapacity'
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
    """Pydantic model for SQL table `LimitGrowthNewCapacityDelta`."""
    __table_name__: ClassVar[str] = 'LimitGrowthNewCapacityDelta'
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
    """Pydantic model for SQL table `LimitDegrowthNewCapacityDelta`."""
    __table_name__: ClassVar[str] = 'LimitDegrowthNewCapacityDelta'
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
    """Pydantic model for SQL table `LimitStorageLevelFraction`."""
    __table_name__: ClassVar[str] = 'LimitStorageLevelFraction'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'season', 'tod', 'tech', 'vintage', 'operator', 'data_id')
    region: str = ...
    period: int = ...
    season: str = ...
    tod: str = ...
    tech: str = ...
    vintage: int = ...
    operator: OperatorCode = OperatorCode.LE
    fraction: float | None = None
    notes: str | None = None
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...


class LimitActivity(CanoeBaseModel):
    """Pydantic model for SQL table `LimitActivity`."""
    __table_name__: ClassVar[str] = 'LimitActivity'
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
    """Pydantic model for SQL table `LimitActivityShare`."""
    __table_name__: ClassVar[str] = 'LimitActivityShare'
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
    """Pydantic model for SQL table `LimitAnnualCapacityFactor`."""
    __table_name__: ClassVar[str] = 'LimitAnnualCapacityFactor'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'tech', 'output_comm', 'operator', 'data_id')
    region: str = ...
    period: int = ...
    tech: str = ...
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
    """Pydantic model for SQL table `LimitCapacity`."""
    __table_name__: ClassVar[str] = 'LimitCapacity'
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
    """Pydantic model for SQL table `LimitCapacityShare`."""
    __table_name__: ClassVar[str] = 'LimitCapacityShare'
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
    """Pydantic model for SQL table `LimitNewCapacity`."""
    __table_name__: ClassVar[str] = 'LimitNewCapacity'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'tech_or_group', 'operator', 'data_id')
    region: str = ...
    period: int = ...
    tech_or_group: str = ...
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
    """Pydantic model for SQL table `LimitNewCapacityShare`."""
    __table_name__: ClassVar[str] = 'LimitNewCapacityShare'
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


class LimitResource(CanoeBaseModel):
    """Pydantic model for SQL table `LimitResource`."""
    __table_name__: ClassVar[str] = 'LimitResource'
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
    """Pydantic model for SQL table `LimitSeasonalCapacityFactor`."""
    __table_name__: ClassVar[str] = 'LimitSeasonalCapacityFactor'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'season', 'tech', 'operator', 'data_id')
    region: str = ...
    period: int = ...
    season: str = ...
    tech: str = ...
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
    """Pydantic model for SQL table `LimitTechInputSplit`."""
    __table_name__: ClassVar[str] = 'LimitTechInputSplit'
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
    """Pydantic model for SQL table `LimitTechInputSplitAnnual`."""
    __table_name__: ClassVar[str] = 'LimitTechInputSplitAnnual'
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
    """Pydantic model for SQL table `LimitTechOutputSplit`."""
    __table_name__: ClassVar[str] = 'LimitTechOutputSplit'
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
    """Pydantic model for SQL table `LimitTechOutputSplitAnnual`."""
    __table_name__: ClassVar[str] = 'LimitTechOutputSplitAnnual'
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
    """Pydantic model for SQL table `LimitEmission`."""
    __table_name__: ClassVar[str] = 'LimitEmission'
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
    """Pydantic model for SQL table `LinkedTech`."""
    __table_name__: ClassVar[str] = 'LinkedTech'
    __primary_key__: ClassVar[tuple[str, ...]] = ('primary_region', 'primary_tech', 'emis_comm', 'data_id')
    primary_region: str = ...
    primary_tech: str = ...
    emis_comm: str = ...
    driven_tech: str | None = None
    notes: str | None = None
    data_id: str = ...


class PlanningReserveMargin(CanoeBaseModel):
    """Pydantic model for SQL table `PlanningReserveMargin`."""
    __table_name__: ClassVar[str] = 'PlanningReserveMargin'
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
    """Pydantic model for SQL table `RampDownHourly`."""
    __table_name__: ClassVar[str] = 'RampDownHourly'
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
    """Pydantic model for SQL table `RampUpHourly`."""
    __table_name__: ClassVar[str] = 'RampUpHourly'
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


class Region(CanoeBaseModel):
    """Pydantic model for SQL table `Region`."""
    __table_name__: ClassVar[str] = 'Region'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region',)
    region: str = ...
    notes: str | None = None


class ReserveCapacityDerate(CanoeBaseModel):
    """Pydantic model for SQL table `ReserveCapacityDerate`."""
    __table_name__: ClassVar[str] = 'ReserveCapacityDerate'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'period', 'season', 'tech', 'vintage', 'data_id')
    region: str = ...
    period: int = ...
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


class TimeSegmentFraction(CanoeBaseModel):
    """Pydantic model for SQL table `TimeSegmentFraction`."""
    __table_name__: ClassVar[str] = 'TimeSegmentFraction'
    __primary_key__: ClassVar[tuple[str, ...]] = ('period', 'season', 'tod')
    period: int = ...
    season: str = ...
    tod: str = ...
    segfrac: float | None = Field(None, ge=0, le=1)
    notes: str | None = None


class StorageDuration(CanoeBaseModel):
    """Pydantic model for SQL table `StorageDuration`."""
    __table_name__: ClassVar[str] = 'StorageDuration'
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
    """Pydantic model for SQL table `LifetimeSurvivalCurve`."""
    __table_name__: ClassVar[str] = 'LifetimeSurvivalCurve'
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


class TechnologyType(CanoeBaseModel):
    """Pydantic model for SQL table `TechnologyType`."""
    __table_name__: ClassVar[str] = 'TechnologyType'
    __primary_key__: ClassVar[tuple[str, ...]] = ('label',)
    label: str = ...
    description: str | None = None


class TimeOfDay(CanoeBaseModel):
    """Pydantic model for SQL table `TimeOfDay`."""
    __table_name__: ClassVar[str] = 'TimeOfDay'
    __primary_key__: ClassVar[tuple[str, ...]] = ('tod',)
    sequence: int | None = None
    tod: str = ...


class TimePeriod(CanoeBaseModel):
    """Pydantic model for SQL table `TimePeriod`."""
    __table_name__: ClassVar[str] = 'TimePeriod'
    __primary_key__: ClassVar[tuple[str, ...]] = ('period',)
    sequence: int | None = None
    period: int = ...
    flag: TimePeriodTypeCode | None = None


class TimeSeason(CanoeBaseModel):
    """Pydantic model for SQL table `TimeSeason`."""
    __table_name__: ClassVar[str] = 'TimeSeason'
    __primary_key__: ClassVar[tuple[str, ...]] = ('period', 'sequence', 'season')
    period: int = ...
    sequence: int = ...
    season: str = ...
    notes: str | None = None


class TimeSeasonSequential(CanoeBaseModel):
    """Pydantic model for SQL table `TimeSeasonSequential`."""
    __table_name__: ClassVar[str] = 'TimeSeasonSequential'
    __primary_key__: ClassVar[tuple[str, ...]] = ('period', 'sequence', 'seas_seq', 'season')
    period: int = ...
    sequence: int = ...
    seas_seq: str = ...
    season: str = ...
    num_days: float = Field(..., gt=0)
    notes: str | None = None


class TimePeriodType(CanoeBaseModel):
    """Pydantic model for SQL table `TimePeriodType`."""
    __table_name__: ClassVar[str] = 'TimePeriodType'
    __primary_key__: ClassVar[tuple[str, ...]] = ('label',)
    label: str = ...
    description: str | None = None


class RPSRequirement(CanoeBaseModel):
    """Pydantic model for SQL table `RPSRequirement`."""
    __table_name__: ClassVar[str] = 'RPSRequirement'
    __primary_key__: ClassVar[tuple[str, ...]] = ('region', 'data_id')
    region: str = ...
    period: int = ...
    tech_group: str = ...
    requirement: float = ...
    data_source: str | None = None
    dq_cred: DataQualityCredibilityLevel | None = None
    dq_geog: DataQualityGeographyLevel | None = None
    dq_struc: DataQualityStructureLevel | None = None
    dq_tech: DataQualityTechnologyLevel | None = None
    dq_time: DataQualityTimeLevel | None = None
    data_id: str = ...
    notes: str | None = None


class TechGroupMember(CanoeBaseModel):
    """Pydantic model for SQL table `TechGroupMember`."""
    __table_name__: ClassVar[str] = 'TechGroupMember'
    __primary_key__: ClassVar[tuple[str, ...]] = ('group_name', 'tech', 'data_id')
    group_name: str = ...
    tech: str = ...
    data_id: str = ...


class Technology(CanoeBaseModel):
    """Pydantic model for SQL table `Technology`."""
    __table_name__: ClassVar[str] = 'Technology'
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


class DataSource(CanoeBaseModel):
    """Pydantic model for SQL table `DataSource`."""
    __table_name__: ClassVar[str] = 'DataSource'
    __primary_key__: ClassVar[tuple[str, ...]] = ('source_id', 'data_id')
    source_id: str = ...
    source: str | None = None
    notes: str | None = None
    data_id: str = ...


class DataQualityCredibility(CanoeBaseModel):
    """Pydantic model for SQL table `DataQualityCredibility`."""
    __table_name__: ClassVar[str] = 'DataQualityCredibility'
    __primary_key__: ClassVar[tuple[str, ...]] = ('dq_cred',)
    dq_cred: DataQualityCredibilityLevel = ...
    description: str | None = None


class DataQualityGeography(CanoeBaseModel):
    """Pydantic model for SQL table `DataQualityGeography`."""
    __table_name__: ClassVar[str] = 'DataQualityGeography'
    __primary_key__: ClassVar[tuple[str, ...]] = ('dq_geog',)
    dq_geog: DataQualityGeographyLevel = ...
    description: str | None = None


class DataQualityStructure(CanoeBaseModel):
    """Pydantic model for SQL table `DataQualityStructure`."""
    __table_name__: ClassVar[str] = 'DataQualityStructure'
    __primary_key__: ClassVar[tuple[str, ...]] = ('dq_struc',)
    dq_struc: DataQualityStructureLevel = ...
    description: str | None = None


class DataQualityTechnology(CanoeBaseModel):
    """Pydantic model for SQL table `DataQualityTechnology`."""
    __table_name__: ClassVar[str] = 'DataQualityTechnology'
    __primary_key__: ClassVar[tuple[str, ...]] = ('dq_tech',)
    dq_tech: DataQualityTechnologyLevel = ...
    description: str | None = None


class DataQualityTime(CanoeBaseModel):
    """Pydantic model for SQL table `DataQualityTime`."""
    __table_name__: ClassVar[str] = 'DataQualityTime'
    __primary_key__: ClassVar[tuple[str, ...]] = ('dq_time',)
    dq_time: DataQualityTimeLevel = ...
    description: str | None = None


class DataSet(CanoeBaseModel):
    """Pydantic model for SQL table `DataSet`."""
    __table_name__: ClassVar[str] = 'DataSet'
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


__all__ = ['CanoeBaseModel', 'MetaData', 'MetaDataReal', 'SeasonLabel', 'SectorLabel', 'CapacityCredit', 'CapacityFactorProcess', 'CapacityFactorTech', 'CapacityToActivity', 'Commodity', 'CommodityType', 'ConstructionInput', 'CostEmission', 'CostFixed', 'CostInvest', 'CostVariable', 'Demand', 'DemandSpecificDistribution', 'EndOfLifeOutput', 'Efficiency', 'EfficiencyVariable', 'EmissionActivity', 'EmissionEmbodied', 'EmissionEndOfLife', 'ExistingCapacity', 'TechGroup', 'LoanLifetimeProcess', 'LoanRate', 'LifetimeProcess', 'LifetimeTech', 'Operator', 'LimitGrowthCapacity', 'LimitDegrowthCapacity', 'LimitGrowthNewCapacity', 'LimitDegrowthNewCapacity', 'LimitGrowthNewCapacityDelta', 'LimitDegrowthNewCapacityDelta', 'LimitStorageLevelFraction', 'LimitActivity', 'LimitActivityShare', 'LimitAnnualCapacityFactor', 'LimitCapacity', 'LimitCapacityShare', 'LimitNewCapacity', 'LimitNewCapacityShare', 'LimitResource', 'LimitSeasonalCapacityFactor', 'LimitTechInputSplit', 'LimitTechInputSplitAnnual', 'LimitTechOutputSplit', 'LimitTechOutputSplitAnnual', 'LimitEmission', 'LinkedTech', 'PlanningReserveMargin', 'RampDownHourly', 'RampUpHourly', 'Region', 'ReserveCapacityDerate', 'TimeSegmentFraction', 'StorageDuration', 'LifetimeSurvivalCurve', 'TechnologyType', 'TimeOfDay', 'TimePeriod', 'TimeSeason', 'TimeSeasonSequential', 'TimePeriodType', 'RPSRequirement', 'TechGroupMember', 'Technology', 'DataSource', 'DataQualityCredibility', 'DataQualityGeography', 'DataQualityStructure', 'DataQualityTechnology', 'DataQualityTime', 'DataSet']
