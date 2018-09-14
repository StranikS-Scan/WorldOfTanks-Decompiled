# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleTimerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleTimerMeta(BaseDAAPIComponent):

    def as_setTotalTimeS(self, minutes, seconds):
        return self.flashObject.as_setTotalTime(minutes, seconds) if self._isDAAPIInited() else None

    def as_setColorS(self, criticalColor):
        return self.flashObject.as_setColor(criticalColor) if self._isDAAPIInited() else None

    def as_showBattleTimerS(self, show):
        return self.flashObject.as_showBattleTimer(show) if self._isDAAPIInited() else None
