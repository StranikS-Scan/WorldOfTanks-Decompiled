# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/common/historical_battles_common/hb_roster_config.py
from UnitRoster import BaseUnitRoster, BaseUnitRosterLimits
from unit_roster_config import RosterSlot10

class HistoricalBattlesRoster(BaseUnitRoster):
    MAX_SLOTS = 5
    MAX_EMPTY_SLOTS = 4
    SLOT_TYPE = RosterSlot10
    DEFAULT_SLOT_PACK = RosterSlot10().pack()
    LIMITS_TYPE = BaseUnitRosterLimits
