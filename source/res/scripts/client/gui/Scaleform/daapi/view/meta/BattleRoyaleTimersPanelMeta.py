# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleRoyaleTimersPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleRoyaleTimersPanelMeta(BaseDAAPIComponent):

    def as_setIsReplayS(self, value):
        return self.flashObject.as_setIsReplay(value) if self._isDAAPIInited() else None

    def as_setRespawnTimeS(self, time):
        return self.flashObject.as_setRespawnTime(time) if self._isDAAPIInited() else None

    def as_setAirDropTimeS(self, time):
        return self.flashObject.as_setAirDropTime(time) if self._isDAAPIInited() else None
