# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortBuildingCardPopoverMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortBuildingCardPopoverMeta(DAAPIModule):

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
