# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/battle/shared/prebattle_timer.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.battle.shared.battle_timers import PreBattleTimer
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.impl import backport
from gui.impl.gen import R
from helpers import i18n

class FortrushPrebattleTimer(PreBattleTimer):
    _STATE_TO_MESSAGE = {COUNTDOWN_STATE.WAIT: R.strings.ingame_gui.timer.waiting(),
     COUNTDOWN_STATE.START: R.strings.ingame_gui.timer.starting(),
     COUNTDOWN_STATE.STOP: R.strings.ingame_gui.timer.started()}

    def _getMessage(self):
        if self._state in (COUNTDOWN_STATE.WAIT, COUNTDOWN_STATE.START):
            msg = backport.text(self._STATE_TO_MESSAGE[self._state])
        else:
            msg = i18n.makeString(self._battleTypeStr)
        return msg

    def setCountdown(self, state, timeLeft):
        super(FortrushPrebattleTimer, self).setCountdown(state, timeLeft)
        if state != COUNTDOWN_STATE.WAIT and timeLeft is not None:
            self._clearTimeShiftCallback()
            self.as_setTimerS(timeLeft)
        return
