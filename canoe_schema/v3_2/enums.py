from __future__ import annotations

from enum import IntEnum, StrEnum

class CommodityTypeCode(StrEnum):
    S = 's'
    A = 'a'
    P = 'p'
    D = 'd'
    E = 'e'
    W = 'w'
    WA = 'wa'
    WP = 'wp'

class OperatorCode(StrEnum):
    E = 'e'
    LE = 'le'
    GE = 'ge'

class TechnologyTypeCode(StrEnum):
    P = 'p'
    PB = 'pb'
    PS = 'ps'

class TimePeriodTypeCode(StrEnum):
    E = 'e'
    F = 'f'

class DataQualityCredibilityLevel(IntEnum):
    EXCELLENT = 1
    GOOD = 2
    ACCEPTABLE = 3
    LACKING = 4
    UNACCEPTABLE = 5

class DataQualityGeographyLevel(IntEnum):
    EXCELLENT = 1
    GOOD = 2
    ACCEPTABLE = 3
    LACKING = 4
    UNACCEPTABLE = 5

class DataQualityStructureLevel(IntEnum):
    EXCELLENT = 1
    GOOD = 2
    ACCEPTABLE = 3
    LACKING = 4
    UNACCEPTABLE = 5

class DataQualityTechnologyLevel(IntEnum):
    EXCELLENT = 1
    GOOD = 2
    ACCEPTABLE = 3
    LACKING = 4
    UNACCEPTABLE = 5

class DataQualityTimeLevel(IntEnum):
    EXCELLENT = 1
    GOOD = 2
    ACCEPTABLE = 3
    LACKING = 4
    UNACCEPTABLE = 5

__all__ = ['CommodityTypeCode', 'OperatorCode', 'TechnologyTypeCode', 'TimePeriodTypeCode', 'DataQualityCredibilityLevel', 'DataQualityGeographyLevel', 'DataQualityStructureLevel', 'DataQualityTechnologyLevel', 'DataQualityTimeLevel']
