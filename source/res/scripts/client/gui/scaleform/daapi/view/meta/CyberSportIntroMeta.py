# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CyberSportIntroMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyIntroView import BaseRallyIntroView

class CyberSportIntroMeta(BaseRallyIntroView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseRallyIntroView
    """

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

    def as_setSelectedVehicleS(self, data):
        """
        :param data: Represented by IntroVehicleVO (AS)
        """
        return self.flashObject.as_setSelectedVehicle(data) if self._isDAAPIInited() else None

    def as_setTextsS(self, data):
        """
        :param data: Represented by CSIntroViewTextsVO (AS)
        """
        return self.flashObject.as_setTexts(data) if self._isDAAPIInited() else None

    def as_setStaticTeamDataS(self, data):
        """
        :param data: Represented by CSIntroViewStaticTeamVO (AS)
        """
        return self.flashObject.as_setStaticTeamData(data) if self._isDAAPIInited() else None

    def as_setNoVehiclesS(self, warnTooltip):
        return self.flashObject.as_setNoVehicles(warnTooltip) if self._isDAAPIInited() else None
