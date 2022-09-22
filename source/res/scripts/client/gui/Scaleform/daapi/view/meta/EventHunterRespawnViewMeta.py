# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventHunterRespawnViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventHunterRespawnViewMeta(BaseDAAPIComponent):

    def onRespawnPointClick(self, id):
        self._printOverrideError('onRespawnPointClick')

    def as_updateTimerS(self, timeLeft, timeTotal, replaySpeed=1):
        return self.flashObject.as_updateTimer(timeLeft, timeTotal, replaySpeed) if self._isDAAPIInited() else None

    def as_setIconS(self, icon):
        return self.flashObject.as_setIcon(icon) if self._isDAAPIInited() else None
