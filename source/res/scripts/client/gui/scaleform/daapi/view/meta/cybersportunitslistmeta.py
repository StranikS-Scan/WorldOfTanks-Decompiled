# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CyberSportUnitsListMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyListView import BaseRallyListView

class CyberSportUnitsListMeta(BaseRallyListView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseRallyListView
    """

    def getTeamData(self, index):
        self._printOverrideError('getTeamData')

    def refreshTeams(self):
        self._printOverrideError('refreshTeams')

    def filterVehicles(self):
        self._printOverrideError('filterVehicles')

    def loadPrevious(self):
        self._printOverrideError('loadPrevious')

    def loadNext(self):
        self._printOverrideError('loadNext')

    def as_setDummyS(self, data):
        """
        :param data: Represented by DummyVO (AS)
        """
        return self.flashObject.as_setDummy(data) if self._isDAAPIInited() else None

    def as_setDummyVisibleS(self, visible):
        return self.flashObject.as_setDummyVisible(visible) if self._isDAAPIInited() else None

    def as_setHeaderS(self, data):
        """
        :param data: Represented by UnitListViewHeaderVO (AS)
        """
        return self.flashObject.as_setHeader(data) if self._isDAAPIInited() else None

    def as_updateNavigationBlockS(self, data):
        """
        :param data: Represented by NavigationBlockVO (AS)
        """
        return self.flashObject.as_updateNavigationBlock(data) if self._isDAAPIInited() else None

    def as_updateRallyIconS(self, iconPath):
        return self.flashObject.as_updateRallyIcon(iconPath) if self._isDAAPIInited() else None
