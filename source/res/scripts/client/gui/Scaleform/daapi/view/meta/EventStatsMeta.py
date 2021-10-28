# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventStatsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventStatsMeta(BaseDAAPIComponent):

    def as_updatePlayerStatsS(self, data):
        return self.flashObject.as_updatePlayerStats(data) if self._isDAAPIInited() else None

    def as_updateDataS(self, title, desc, difficulty, goal):
        return self.flashObject.as_updateData(title, desc, difficulty, goal) if self._isDAAPIInited() else None

    def as_updateBuffsS(self, data):
        return self.flashObject.as_updateBuffs(data) if self._isDAAPIInited() else None
