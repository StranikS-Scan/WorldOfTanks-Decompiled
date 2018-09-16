# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/period_music_listener.py
import WWISE
from constants import ARENA_PERIOD
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView

class PeriodMusicListener(IAbstractPeriodView):
    _ARENA_PERIOD_STATE = {ARENA_PERIOD.WAITING: 'STATE_arenastate_waiting',
     ARENA_PERIOD.PREBATTLE: 'STATE_arenastate_counter',
     ARENA_PERIOD.BATTLE: 'STATE_arenastate_battle'}
    _STATE_ID = 'STATE_arenastate'

    def setPeriod(self, period):
        state_value = self._ARENA_PERIOD_STATE.get(period, None)
        if state_value is not None:
            WWISE.WW_setState(self._STATE_ID, state_value)
        return
