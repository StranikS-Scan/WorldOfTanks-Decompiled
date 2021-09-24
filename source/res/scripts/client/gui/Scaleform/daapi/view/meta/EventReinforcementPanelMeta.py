# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventReinforcementPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventReinforcementPanelMeta(BaseDAAPIComponent):

    def as_setPlayerLivesS(self, count):
        return self.flashObject.as_setPlayerLives(count) if self._isDAAPIInited() else None
