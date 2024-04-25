# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/battle_timers.py
from gui.Scaleform.daapi.view.battle.shared.battle_timers import PreBattleTimer
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.impl import backport
from gui.impl.gen import R

class HistoricalBattlesPreBattleTimer(PreBattleTimer):
    _ALT_MESSAGE_TIME = 2

    def setCountdown(self, state, timeLeft):
        super(HistoricalBattlesPreBattleTimer, self).setCountdown(state, timeLeft)
        if timeLeft <= self._ALT_MESSAGE_TIME:
            self.as_setMessageS(backport.text(R.strings.ingame_gui.timer.started()))

    def _getMessage(self):
        return backport.text(R.strings.hb_battle.battleTimer.waiting()) if self._state == COUNTDOWN_STATE.WAIT else backport.text(R.strings.hb_battle.battleTimer.defend())

    def _isDisplayWinCondition(self):
        return False
