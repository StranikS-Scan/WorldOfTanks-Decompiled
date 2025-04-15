# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/meta/FrontlineBattleTimerMeta.py
from gui.Scaleform.daapi.view.battle.shared.battle_timers import BattleTimer

class FrontlineBattleTimerMeta(BattleTimer):

    def as_setTotalTimeWithSecondsS(self, minutes, seconds, timeFactor):
        return self.flashObject.as_setTotalTimeWithSeconds(minutes, seconds, timeFactor) if self._isDAAPIInited() else None

    def as_enableOvertimeS(self, enabled):
        return self.flashObject.as_enableOvertime(enabled) if self._isDAAPIInited() else None
