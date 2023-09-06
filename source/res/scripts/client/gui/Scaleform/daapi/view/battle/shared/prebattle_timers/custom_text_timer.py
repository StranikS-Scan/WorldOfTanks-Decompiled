# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/prebattle_timers/custom_text_timer.py
from helpers.i18n import makeString
from timer_base import PreBattleTimerBase
from gui.battle_control.battle_constants import COUNTDOWN_STATE
_g_timerSettings = {}

class CustomTextPrebattleTimer(PreBattleTimerBase):

    def __init__(self):
        super(CustomTextPrebattleTimer, self).__init__()
        self.wasCustomWinConditionAdded = False

    def updateBattleCtx(self, battleCtx):
        self._battleTypeStr = battleCtx.getArenaDescriptionString(isInBattle=False)
        self.as_setMessageS(self._getMessage())

    def setCountdown(self, state, timeLeft):
        if not self.wasCustomWinConditionAdded:
            if _g_timerSettings:
                msg = makeString(_g_timerSettings.get('subheader', ''))
                self.as_setWinConditionTextS(msg)
                self.as_setMessageS(self._getMessage())
                self.wasCustomWinConditionAdded = True
        super(CustomTextPrebattleTimer, self).setCountdown(state, timeLeft)

    def hideCountdown(self, state, speed):
        if _g_timerSettings:
            msg = makeString(_g_timerSettings.get('battleStartMessage', ''))
            self.as_setMessageS(msg)
            self._clearTimeShiftCallback()
            self.as_hideAllS(speed != 0)
        else:
            super(CustomTextPrebattleTimer, self).hideCountdown(state, speed)

    def _getMessage(self):
        if self._state == COUNTDOWN_STATE.WAIT:
            msg = super(CustomTextPrebattleTimer, self)._getMessage()
        elif _g_timerSettings:
            msg = makeString(_g_timerSettings.get('header', ''))
        else:
            msg = super(CustomTextPrebattleTimer, self)._getMessage()
        return msg

    def _dispose(self):
        _g_timerSettings.clear()
        super(CustomTextPrebattleTimer, self)._dispose()


def setTimerSettings(header, message, subheader=None):
    _g_timerSettings['header'] = header
    _g_timerSettings['battleStartMessage'] = message
    if subheader is not None:
        _g_timerSettings['subheader'] = subheader
    return
