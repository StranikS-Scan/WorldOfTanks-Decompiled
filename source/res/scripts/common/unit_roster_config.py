# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/unit_roster_config.py
from constants import IS_CHINA, VEHICLE_CLASSES
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


class EpicSlot(BaseUnitRosterSlot):
    DEFAULT_LEVELS = (8, 9)


class Comp7Slot(BaseUnitRosterSlot):
    DEFAULT_LEVELS = (10, 10)


class SquadRoster(BaseUnitRoster):
    MAX_SLOTS = 3
    MAX_EMPTY_SLOTS = 2
    SLOT_TYPE = RosterSlot10
    DEFAULT_SLOT_PACK = RosterSlot10().pack()
    LIMITS_TYPE = BaseUnitRosterLimits


class SpecRoster(BaseUnitRoster):
    MAX_SLOTS = 15
    MAX_EMPTY_SLOTS = 14
    SLOT_TYPE = RosterSlot10
    DEFAULT_SLOT_PACK = RosterSlot10().pack()
    MAX_UNIT_POINTS_SUM = 150
    LIMITS_TYPE = BaseUnitRosterLimits


class EventRoster(BaseUnitRoster):
    MAX_SLOTS = 5
    MAX_EMPTY_SLOTS = 4
    SLOT_TYPE = RosterSlot10
    DEFAULT_SLOT_PACK = RosterSlot10().pack()
    LIMITS_TYPE = BaseUnitRosterLimits


class EpicRoster(BaseUnitRoster):
    MAX_SLOTS = 3
    MAX_EMPTY_SLOTS = 2
    SLOT_TYPE = EpicSlot
    DEFAULT_SLOT_PACK = EpicSlot().pack()
    LIMITS_TYPE = BaseUnitRosterLimits
    MIN_VEHICLES = 1
    MAX_VEHICLES = 10000


class BattleRoyaleRoster(BaseUnitRoster):
    MAX_SLOTS = 2
    MAX_EMPTY_SLOTS = 1
    SLOT_TYPE = RosterSlot10
    DEFAULT_SLOT_PACK = RosterSlot10().pack()
    LIMITS_TYPE = BaseUnitRosterLimits


class MapBoxRoster(BaseUnitRoster):
    MAX_SLOTS = 3
    MAX_EMPTY_SLOTS = 2
    SLOT_TYPE = RosterSlot10
    DEFAULT_SLOT_PACK = RosterSlot10().pack()
    LIMITS_TYPE = BaseUnitRosterLimits


class FunRandomRoster(BaseUnitRoster):
    MAX_SLOTS = 3
    MAX_EMPTY_SLOTS = 2
    SLOT_TYPE = RosterSlot10
    DEFAULT_SLOT_PACK = RosterSlot10().pack()
    LIMITS_TYPE = BaseUnitRosterLimits


class Comp7Roster(BaseUnitRoster):
    MAX_SLOTS = 7
    MAX_EMPTY_SLOTS = 6
    SLOT_TYPE = Comp7Slot
    DEFAULT_SLOT_PACK = Comp7Slot().pack()
    LIMITS_TYPE = BaseUnitRosterLimits
    MAX_VEHICLES = 10000
