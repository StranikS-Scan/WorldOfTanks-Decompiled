# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CyberSportUnitsListMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyListView import BaseRallyListView

class CyberSportUnitsListMeta(BaseRallyListView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseRallyListView
    null
    """

    def getTeamData(self, index):
        """
        :param index:
        :return Object:
        """
        self._printOverrideError('getTeamData')

    def refreshTeams(self):
        """
        :return :
        """
        self._printOverrideError('refreshTeams')

    def filterVehicles(self):
        """
        :return :
        """
        self._printOverrideError('filterVehicles')

    def setTeamFilters(self, showOnlyStatic):
        """
        :param showOnlyStatic:
        :return :
        """
        self._printOverrideError('setTeamFilters')

    def loadPrevious(self):
        """
        :return :
        """
        self._printOverrideError('loadPrevious')

    def loadNext(self):
        """
        :return :
        """
        self._printOverrideError('loadNext')

    def showRallyProfile(self, id):
        """
        :param id:
        :return :
        """
        self._printOverrideError('showRallyProfile')

    def searchTeams(self, name):
        """
        :param name:
        :return :
        """
        self._printOverrideError('searchTeams')

    def as_setDummyS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setDummy(data) if self._isDAAPIInited() else None

    def as_setDummyVisibleS(self, visible):
        """
        :param visible:
        :return :
        """
        return self.flashObject.as_setDummyVisible(visible) if self._isDAAPIInited() else None

    def as_setSearchResultTextS(self, text, descrText, filterData):
        """
        :param text:
        :param descrText:
        :param filterData:
        :return :
        """
        return self.flashObject.as_setSearchResultText(text, descrText, filterData) if self._isDAAPIInited() else None

    def as_setHeaderS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setHeader(data) if self._isDAAPIInited() else None

    def as_updateNavigationBlockS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_updateNavigationBlock(data) if self._isDAAPIInited() else None

    def as_updateRallyIconS(self, iconPath):
        """
        :param iconPath:
        :return :
        """
        return self.flashObject.as_updateRallyIcon(iconPath) if self._isDAAPIInited() else None
