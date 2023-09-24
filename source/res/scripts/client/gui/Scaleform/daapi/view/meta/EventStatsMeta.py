# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventStatsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventStatsMeta(BaseDAAPIComponent):

    def as_updatePlayerStatsS(self, data):
        return self.flashObject.as_updatePlayerStats(data) if self._isDAAPIInited() else None

    def as_updateTitleS(self, title, desc):
        return self.flashObject.as_updateTitle(title, desc) if self._isDAAPIInited() else None
