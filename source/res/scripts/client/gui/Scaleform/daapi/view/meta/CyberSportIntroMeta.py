# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CyberSportIntroMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyIntroView import BaseRallyIntroView

class CyberSportIntroMeta(BaseRallyIntroView):

    def requestVehicleSelection(self):
        self._printOverrideError('requestVehicleSelection')

    def startAutoMatching(self):
        self._printOverrideError('startAutoMatching')

    def showSelectorPopup(self):
        self._printOverrideError('showSelectorPopup')

    def showStaticTeamProfile(self):
        self._printOverrideError('showStaticTeamProfile')

    def cancelWaitingTeamRequest(self):
        self._printOverrideError('cancelWaitingTeamRequest')

    def showStaticTeamStaff(self):
        self._printOverrideError('showStaticTeamStaff')

    def joinClubUnit(self):
        self._printOverrideError('joinClubUnit')

    def as_setSelectedVehicleS(self, selectedVehicleData, selectedVehicleIsReady, warnTooltip):
        return self.flashObject.as_setSelectedVehicle(selectedVehicleData, selectedVehicleIsReady, warnTooltip) if self._isDAAPIInited() else None

    def as_setTextsS(self, data):
        return self.flashObject.as_setTexts(data) if self._isDAAPIInited() else None

    def as_setStaticTeamDataS(self, data):
        return self.flashObject.as_setStaticTeamData(data) if self._isDAAPIInited() else None

    def as_setNoVehiclesS(self, warnTooltip):
        return self.flashObject.as_setNoVehicles(warnTooltip) if self._isDAAPIInited() else None
