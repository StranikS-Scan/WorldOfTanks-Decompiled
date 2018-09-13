# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CyberSportUnitsListMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyListView import BaseRallyListView

class CyberSportUnitsListMeta(BaseRallyListView):

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

    def as_setSearchResultTextS(self, text):
        if self._isDAAPIInited():
            return self.flashObject.as_setSearchResultText(text)

    def as_setSelectedVehiclesInfoS(self, infoText, selectedVehiclesCount):
        if self._isDAAPIInited():
            return self.flashObject.as_setSelectedVehiclesInfo(infoText, selectedVehiclesCount)

    def as_updateNavigationBlockS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_updateNavigationBlock(value)
