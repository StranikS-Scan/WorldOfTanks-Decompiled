# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CyberSportIntroMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyIntroView import BaseRallyIntroView

class CyberSportIntroMeta(BaseRallyIntroView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseRallyIntroView
    null
    """

    def requestVehicleSelection(self):
        """
        :return :
        """
        self._printOverrideError('requestVehicleSelection')

    def startAutoMatching(self):
        """
        :return :
        """
        self._printOverrideError('startAutoMatching')

    def showSelectorPopup(self):
        """
        :return :
        """
        self._printOverrideError('showSelectorPopup')

    def showStaticTeamProfile(self):
        """
        :return :
        """
        self._printOverrideError('showStaticTeamProfile')

    def cancelWaitingTeamRequest(self):
        """
        :return :
        """
        self._printOverrideError('cancelWaitingTeamRequest')

    def showStaticTeamStaff(self):
        """
        :return :
        """
        self._printOverrideError('showStaticTeamStaff')

    def joinClubUnit(self):
        """
        :return :
        """
        self._printOverrideError('joinClubUnit')

    def as_setSelectedVehicleS(self, selectedVehicleData, selectedVehicleIsReady, warnTooltip):
        """
        :param selectedVehicleData:
        :param selectedVehicleIsReady:
        :param warnTooltip:
        :return :
        """
        return self.flashObject.as_setSelectedVehicle(selectedVehicleData, selectedVehicleIsReady, warnTooltip) if self._isDAAPIInited() else None

    def as_setTextsS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setTexts(data) if self._isDAAPIInited() else None

    def as_setStaticTeamDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setStaticTeamData(data) if self._isDAAPIInited() else None

    def as_setNoVehiclesS(self, warnTooltip):
        """
        :param warnTooltip:
        :return :
        """
        return self.flashObject.as_setNoVehicles(warnTooltip) if self._isDAAPIInited() else None
