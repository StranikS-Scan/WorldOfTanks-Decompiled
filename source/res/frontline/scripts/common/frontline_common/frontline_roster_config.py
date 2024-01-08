# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/common/frontline_common/frontline_roster_config.py
from UnitRoster import BaseUnitRoster, BaseUnitRosterLimits, BaseUnitRosterSlot

class EpicSlot(BaseUnitRosterSlot):
    DEFAULT_LEVELS = (8, 9)


class EpicRoster(BaseUnitRoster):
    MAX_SLOTS = 3
    MAX_EMPTY_SLOTS = 2
    SLOT_TYPE = EpicSlot
    DEFAULT_SLOT_PACK = EpicSlot().pack()
    LIMITS_TYPE = BaseUnitRosterLimits
    MIN_VEHICLES = 1
    MAX_VEHICLES = 10000
