# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/common/white_tiger_common/wt_roster_config.py
from UnitRoster import BaseUnitRoster, BaseUnitRosterLimits
from unit_roster_config import RosterSlot10

class WhiteTigerRoster(BaseUnitRoster):
    MAX_SLOTS = 3
    MAX_EMPTY_SLOTS = 1
    SLOT_TYPE = RosterSlot10
    DEFAULT_SLOT_PACK = RosterSlot10().pack()
    LIMITS_TYPE = BaseUnitRosterLimits
