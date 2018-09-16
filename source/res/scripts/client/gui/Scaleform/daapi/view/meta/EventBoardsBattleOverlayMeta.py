# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBoardsBattleOverlayMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventBoardsBattleOverlayMeta(BaseDAAPIComponent):

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setExperienceDataS(self, data):
        return self.flashObject.as_setExperienceData(data) if self._isDAAPIInited() else None

    def as_setStatisticsDataS(self, data):
        return self.flashObject.as_setStatisticsData(data) if self._isDAAPIInited() else None

    def as_setTableHeaderDataS(self, data):
        return self.flashObject.as_setTableHeaderData(data) if self._isDAAPIInited() else None

    def as_setTableDataS(self, data):
        return self.flashObject.as_setTableData(data) if self._isDAAPIInited() else None
