# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/battle_control/battle_constants.py
from gui.battle_control.battle_constants import TIMER_VIEW_STATE
from death_zones_helpers import ZONE_STATE

class BrTimerViewState(TIMER_VIEW_STATE):
    DAMAGING = 'damaging'

    @staticmethod
    def fromZone(state):
        if state == ZONE_STATE.CRITICAL:
            return BrTimerViewState.CRITICAL
        else:
            return BrTimerViewState.WARNING if state == ZONE_STATE.WARNING else None
