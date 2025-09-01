# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/common/fun_random_common/fun_roster_config.py
from UnitRoster import BaseUnitRoster, BaseUnitRosterLimits
from unit_roster_config import RosterSlot11

class FunRandomRoster(BaseUnitRoster):
    MAX_SLOTS = 3
    MAX_EMPTY_SLOTS = 2
    SLOT_TYPE = RosterSlot11
    DEFAULT_SLOT_PACK = RosterSlot11().pack()
    LIMITS_TYPE = BaseUnitRosterLimits
