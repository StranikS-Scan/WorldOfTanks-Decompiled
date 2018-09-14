# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortBuildingCardPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class FortBuildingCardPopoverMeta(SmartPopOverView):

    def openUpgradeWindow(self, value):
        self._printOverrideError('openUpgradeWindow')

    def openAssignedPlayersWindow(self, value):
        self._printOverrideError('openAssignedPlayersWindow')

    def openDemountBuildingWindow(self, value):
        self._printOverrideError('openDemountBuildingWindow')

    def openDirectionControlWindow(self):
        self._printOverrideError('openDirectionControlWindow')

    def openBuyOrderWindow(self):
        self._printOverrideError('openBuyOrderWindow')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)

    def as_setModernizationDestructionEnablingS(self, modernizationButtonEnabled, destroyButtonEnabled, modernizationButtonTooltip, destroyButtonTooltip):
        if self._isDAAPIInited():
            return self.flashObject.as_setModernizationDestructionEnabling(modernizationButtonEnabled, destroyButtonEnabled, modernizationButtonTooltip, destroyButtonTooltip)
