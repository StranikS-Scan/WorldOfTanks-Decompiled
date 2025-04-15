# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/meta/FrontlineReinforcementPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FrontlineReinforcementPanelMeta(BaseDAAPIComponent):

    def as_setPlayerLivesS(self, lives):
        return self.flashObject.as_setPlayerLives(lives) if self._isDAAPIInited() else None

    def as_setTimestampS(self, timestamp, servertime):
        return self.flashObject.as_setTimestamp(timestamp, servertime) if self._isDAAPIInited() else None

    def as_setTimeS(self, time):
        return self.flashObject.as_setTime(time) if self._isDAAPIInited() else None
