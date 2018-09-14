# Embedded file name: scripts/common/unit_roster_config.py
import fortified_regions, clubs_settings
from UnitBase import BaseUnitRosterSlot
from UnitRoster import BaseUnitRoster

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


class RosterSlot6(BaseUnitRosterSlot):
    DEFAULT_LEVELS = (1, 6)


class RosterSlot8(BaseUnitRosterSlot):
    DEFAULT_LEVELS = (1, 8)


class RosterSlot10(BaseUnitRosterSlot):
    DEFAULT_LEVELS = (1, 10)


class BaseSortieRoster(BaseUnitRoster):

    def getLegionariesMaxCount(self):
        return fortified_regions.g_cache.maxLegionariesCount


class SortieRoster6(BaseSortieRoster):
    MAX_SLOTS = 7
    MAX_EMPTY_SLOTS = 1
    SLOT_TYPE = RosterSlot6
    DEFAULT_SLOT_PACK = RosterSlot6().pack()
    MAX_UNIT_POINTS_SUM = 42


class SortieRoster8(BaseSortieRoster):
    MAX_SLOTS = 10
    MAX_EMPTY_SLOTS = 2
    SLOT_TYPE = RosterSlot8
    DEFAULT_SLOT_PACK = RosterSlot8().pack()
    MAX_UNIT_POINTS_SUM = 80


class SortieRoster10(BaseSortieRoster):
    MAX_SLOTS = 15
    MAX_EMPTY_SLOTS = 3
    SLOT_TYPE = RosterSlot10
    DEFAULT_SLOT_PACK = RosterSlot10().pack()
    MAX_UNIT_POINTS_SUM = 150


class FortRoster8(BaseUnitRoster):
    MAX_SLOTS = 10
    MAX_EMPTY_SLOTS = 9
    SLOT_TYPE = RosterSlot8
    DEFAULT_SLOT_PACK = RosterSlot8().pack()
    MAX_UNIT_POINTS_SUM = 80


class FortRoster10(BaseUnitRoster):
    MAX_SLOTS = 15
    MAX_EMPTY_SLOTS = 14
    SLOT_TYPE = RosterSlot10
    DEFAULT_SLOT_PACK = RosterSlot10().pack()
    MAX_UNIT_POINTS_SUM = 150


class ClubRoster(UnitRoster):

    def getLegionariesMaxCount(self):
        return clubs_settings.g_cache.maxLegionariesCount


class SquadRoster(BaseUnitRoster):
    MAX_SLOTS = 3
    MAX_EMPTY_SLOTS = 2
    SLOT_TYPE = RosterSlot10
    DEFAULT_SLOT_PACK = RosterSlot10().pack()
