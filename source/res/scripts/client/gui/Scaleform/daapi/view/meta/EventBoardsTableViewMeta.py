# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBoardsTableViewMeta.py
from gui.Scaleform.framework.entities.View import View

class EventBoardsTableViewMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def setMyPlace(self):
        self._printOverrideError('setMyPlace')

    def participateStatusClick(self):
        self._printOverrideError('participateStatusClick')

    def playerClick(self, id):
        self._printOverrideError('playerClick')

    def showNextAward(self, visible):
        self._printOverrideError('showNextAward')

    def as_setHeaderDataS(self, data):
        """
        :param data: Represented by EventBoardsTableViewHeaderVO (AS)
        """
        return self.flashObject.as_setHeaderData(data) if self._isDAAPIInited() else None

    def as_setStatusDataS(self, data):
        """
        :param data: Represented by EventBoardsTableViewStatusVO (AS)
        """
        return self.flashObject.as_setStatusData(data) if self._isDAAPIInited() else None

    def as_setTableDataS(self, data):
        """
        :param data: Represented by EventBoardTableRendererContainerVO (AS)
        """
        return self.flashObject.as_setTableData(data) if self._isDAAPIInited() else None

    def as_setTableHeaderDataS(self, data):
        """
        :param data: Represented by EventBoardTableHeaderVO (AS)
        """
        return self.flashObject.as_setTableHeaderData(data) if self._isDAAPIInited() else None

    def as_setBackgroundS(self, source):
        return self.flashObject.as_setBackground(source) if self._isDAAPIInited() else None

    def as_setScrollPosS(self, value):
        return self.flashObject.as_setScrollPos(value) if self._isDAAPIInited() else None

    def as_setMyPlaceVisibleS(self, visible):
        return self.flashObject.as_setMyPlaceVisible(visible) if self._isDAAPIInited() else None

    def as_setMyPlaceS(self, value):
        return self.flashObject.as_setMyPlace(value) if self._isDAAPIInited() else None

    def as_setMyPlaceTooltipS(self, tooltip):
        return self.flashObject.as_setMyPlaceTooltip(tooltip) if self._isDAAPIInited() else None

    def as_setStatusVisibleS(self, visible):
        return self.flashObject.as_setStatusVisible(visible) if self._isDAAPIInited() else None

    def as_setWaitingS(self, visible, message):
        return self.flashObject.as_setWaiting(visible, message) if self._isDAAPIInited() else None

    def as_setMaintenanceS(self, visible, message1, message2, buttonLabel):
        return self.flashObject.as_setMaintenance(visible, message1, message2, buttonLabel) if self._isDAAPIInited() else None

    def as_setAwardsStripesS(self, data):
        """
        :param data: Represented by EventBoardTableRendererContainerVO (AS)
        """
        return self.flashObject.as_setAwardsStripes(data) if self._isDAAPIInited() else None

    def as_setEmptyDataS(self, value):
        return self.flashObject.as_setEmptyData(value) if self._isDAAPIInited() else None
