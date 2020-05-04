# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventStatsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventStatsMeta(BaseDAAPIComponent):

    def as_updatePlayerStatsS(self, data, idx):
        return self.flashObject.as_updatePlayerStats(data, idx) if self._isDAAPIInited() else None
