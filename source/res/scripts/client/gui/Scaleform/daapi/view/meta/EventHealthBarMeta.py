# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventHealthBarMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventHealthBarMeta(BaseDAAPIComponent):

    def as_updateHealthS(self, healthStr, progress):
        return self.flashObject.as_updateHealth(healthStr, progress) if self._isDAAPIInited() else None

    def as_showHealthBarS(self, show):
        return self.flashObject.as_showHealthBar(show) if self._isDAAPIInited() else None
