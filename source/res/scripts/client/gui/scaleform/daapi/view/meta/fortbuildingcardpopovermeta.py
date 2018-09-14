# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortBuildingCardPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class FortBuildingCardPopoverMeta(SmartPopOverView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends SmartPopOverView
    """

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
        """
        :param data: Represented by BuildingCardPopoverVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setModernizationDestructionEnablingS(self, modernizationButtonEnabled, destroyButtonEnabled, modernizationButtonTooltip, destroyButtonTooltip):
        return self.flashObject.as_setModernizationDestructionEnabling(modernizationButtonEnabled, destroyButtonEnabled, modernizationButtonTooltip, destroyButtonTooltip) if self._isDAAPIInited() else None
