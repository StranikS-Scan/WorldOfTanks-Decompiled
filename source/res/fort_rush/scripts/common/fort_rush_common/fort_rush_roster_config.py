# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/common/fort_rush_common/fort_rush_roster_config.py
from __future__ import absolute_import
from UnitRoster import BaseUnitRoster, BaseUnitRosterLimits
from unit_roster_config import RosterSlot10
from fort_rush_common.fort_rush_constants import MAX_ELIGIBLE_VEHICLES

class FortRushRoster(BaseUnitRoster):
    MAX_SLOTS = 3
    MAX_EMPTY_SLOTS = 2
    SLOT_TYPE = RosterSlot10
    DEFAULT_SLOT_PACK = RosterSlot10().pack()
    LIMITS_TYPE = BaseUnitRosterLimits
    MAX_VEHICLES = MAX_ELIGIBLE_VEHICLES
