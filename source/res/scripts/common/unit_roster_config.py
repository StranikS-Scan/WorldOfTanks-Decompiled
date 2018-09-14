# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/unit_roster_config.py
from constants import IS_CHINA
import fortified_regions
import clubs_settings
from UnitRoster import BaseUnitRoster, BaseUnitRosterSlot, BaseUnitRosterLimits

class UnitRosterSlot(BaseUnitRosterSlot):
    DEFAULT_LEVELS = (6, 8)


class UnitRoster(BaseUnitRoster):
    MAX_SLOTS = 7
    MAX_CLOSED_SLOTS = 0
    SLOT_TYPE = UnitRosterSlot
    DEFAULT_SLOT_PACK = UnitRosterSlot().pack()
    MIN_UNIT_POINTS_SUM = 54
    MAX_UNIT_POINTS_SUM = 54
    MAX_UNIT_ASSEMBLER_ARTY = 2
    LIMITS_TYPE = BaseUnitRosterLimits


class RosterSlot6(BaseUnitRosterSlot):
    DEFAULT_LEVELS = (1, 6)


class RosterSlot8(BaseUnitRosterSlot):
    DEFAULT_LEVELS = (1, 8)


class RosterSlot10(BaseUnitRosterSlot):
    DEFAULT_LEVELS = (1, 10)


class SortieSlot6(BaseUnitRosterSlot):
    DEFAULT_LEVELS = (4, 6) if not IS_CHINA else (10, 10)


class SortieSlot8(BaseUnitRosterSlot):
    DEFAULT_LEVELS = (6, 8) if not IS_CHINA else (10, 10)


class SortieSlot10(BaseUnitRosterSlot):
    DEFAULT_LEVELS = (8, 10) if not IS_CHINA else (10, 10)


class BaseSortieRoster(BaseUnitRoster):

    def getLegionariesMaxCount(self):
        return fortified_regions.g_cache.maxLegionariesCount


class SortieRoster6(BaseSortieRoster):
    MAX_SLOTS = 7
    MAX_EMPTY_SLOTS = 1
    SLOT_TYPE = SortieSlot6
    DEFAULT_SLOT_PACK = SortieSlot6().pack()
    MAX_UNIT_POINTS_SUM = 7 * max(SortieSlot6.DEFAULT_LEVELS)
    LIMITS_TYPE = BaseUnitRosterLimits


class SortieRoster8(BaseSortieRoster):
    MAX_SLOTS = 10
    MAX_EMPTY_SLOTS = 2
    SLOT_TYPE = SortieSlot8
    DEFAULT_SLOT_PACK = SortieSlot8().pack()
    MAX_UNIT_POINTS_SUM = 10 * max(SortieSlot8.DEFAULT_LEVELS)
    LIMITS_TYPE = BaseUnitRosterLimits


class SortieRoster10(BaseSortieRoster):
    MAX_SLOTS = 15
    MAX_EMPTY_SLOTS = 3
    SLOT_TYPE = SortieSlot10
    DEFAULT_SLOT_PACK = SortieSlot10().pack()
    MAX_UNIT_POINTS_SUM = 15 * max(SortieSlot10.DEFAULT_LEVELS)
    LIMITS_TYPE = BaseUnitRosterLimits


class FortRoster8(BaseUnitRoster):
    MAX_SLOTS = 10
    MAX_EMPTY_SLOTS = 9
    SLOT_TYPE = RosterSlot8
    DEFAULT_SLOT_PACK = RosterSlot8().pack()
    MAX_UNIT_POINTS_SUM = 80
    LIMITS_TYPE = BaseUnitRosterLimits


class FortRoster10(BaseUnitRoster):
    MAX_SLOTS = 15
    MAX_EMPTY_SLOTS = 14
    SLOT_TYPE = RosterSlot10
    DEFAULT_SLOT_PACK = RosterSlot10().pack()
    MAX_UNIT_POINTS_SUM = 150
    LIMITS_TYPE = BaseUnitRosterLimits


class ClubRoster(UnitRoster):

    def getLegionariesMaxCount(self):
        return clubs_settings.g_cache.maxLegionariesCount


class SquadRoster(BaseUnitRoster):
    MAX_SLOTS = 3
    MAX_EMPTY_SLOTS = 2
    SLOT_TYPE = RosterSlot10
    DEFAULT_SLOT_PACK = RosterSlot10().pack()
    LIMITS_TYPE = BaseUnitRosterLimits


class FalloutClassicRoster(BaseUnitRoster):
    MAX_SLOTS = 3
    MAX_EMPTY_SLOTS = 2
    SLOT_TYPE = RosterSlot10
    DEFAULT_SLOT_PACK = RosterSlot10().pack()
    LIMITS_TYPE = BaseUnitRosterLimits
    MIN_VEHICLES = 3
    MAX_VEHICLES = 3


class FalloutMultiteamRoster(BaseUnitRoster):
    MAX_SLOTS = 3
    MAX_EMPTY_SLOTS = 1
    SLOT_TYPE = RosterSlot10
    DEFAULT_SLOT_PACK = RosterSlot10().pack()
    LIMITS_TYPE = BaseUnitRosterLimits
    MIN_VEHICLES = 1
    MAX_VEHICLES = 3


class SpecRoster(BaseUnitRoster):
    MAX_SLOTS = 15
    MAX_EMPTY_SLOTS = 14
    SLOT_TYPE = RosterSlot10
    DEFAULT_SLOT_PACK = RosterSlot10().pack()
    MAX_UNIT_POINTS_SUM = 150
    LIMITS_TYPE = BaseUnitRosterLimits


class EventRoster(BaseUnitRoster):
    MAX_SLOTS = 3
    MAX_EMPTY_SLOTS = 2
    SLOT_TYPE = RosterSlot10
    DEFAULT_SLOT_PACK = RosterSlot10().pack()
    LIMITS_TYPE = BaseUnitRosterLimits
