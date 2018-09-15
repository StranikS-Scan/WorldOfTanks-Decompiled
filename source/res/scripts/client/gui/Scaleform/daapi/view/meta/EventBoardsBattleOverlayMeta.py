# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBoardsBattleOverlayMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventBoardsBattleOverlayMeta(BaseDAAPIComponent):

    def as_setDataS(self, data):
        """
        :param data: Represented by EventBoardsBattleOverlayVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setExperienceDataS(self, data):
        """
        :param data: Represented by BattleExperienceBlockVO (AS)
        """
        return self.flashObject.as_setExperienceData(data) if self._isDAAPIInited() else None

    def as_setStatisticsDataS(self, data):
        """
        :param data: Represented by BattleStatisticsBlockVO (AS)
        """
        return self.flashObject.as_setStatisticsData(data) if self._isDAAPIInited() else None

    def as_setTableHeaderDataS(self, data):
        """
        :param data: Represented by EventBoardTableHeaderVO (AS)
        """
        return self.flashObject.as_setTableHeaderData(data) if self._isDAAPIInited() else None

    def as_setTableDataS(self, data):
        """
        :param data: Represented by EventBoardTableRendererContainerVO (AS)
        """
        return self.flashObject.as_setTableData(data) if self._isDAAPIInited() else None
