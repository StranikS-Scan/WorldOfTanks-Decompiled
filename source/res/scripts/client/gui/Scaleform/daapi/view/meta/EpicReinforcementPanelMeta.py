# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicReinforcementPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EpicReinforcementPanelMeta(BaseDAAPIComponent):

    def as_setPlayerLivesS(self, lives):
        return self.flashObject.as_setPlayerLives(lives) if self._isDAAPIInited() else None

    def as_setTimestampS(self, timestamp, servertime):
        return self.flashObject.as_setTimestamp(timestamp, servertime) if self._isDAAPIInited() else None

    def as_setTimeS(self, time):
        return self.flashObject.as_setTime(time) if self._isDAAPIInited() else None
