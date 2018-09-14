# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortBuildingCardPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class FortBuildingCardPopoverMeta(SmartPopOverView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends SmartPopOverView
    null
    """

    def openUpgradeWindow(self, value):
        """
        :param value:
        :return :
        """
        self._printOverrideError('openUpgradeWindow')

    def openAssignedPlayersWindow(self, value):
        """
        :param value:
        :return :
        """
        self._printOverrideError('openAssignedPlayersWindow')

    def openDemountBuildingWindow(self, value):
        """
        :param value:
        :return :
        """
        self._printOverrideError('openDemountBuildingWindow')

    def openDirectionControlWindow(self):
        """
        :return :
        """
        self._printOverrideError('openDirectionControlWindow')

    def openBuyOrderWindow(self):
        """
        :return :
        """
        self._printOverrideError('openBuyOrderWindow')

    def as_setDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setModernizationDestructionEnablingS(self, modernizationButtonEnabled, destroyButtonEnabled, modernizationButtonTooltip, destroyButtonTooltip):
        """
        :param modernizationButtonEnabled:
        :param destroyButtonEnabled:
        :param modernizationButtonTooltip:
        :param destroyButtonTooltip:
        :return :
        """
        return self.flashObject.as_setModernizationDestructionEnabling(modernizationButtonEnabled, destroyButtonEnabled, modernizationButtonTooltip, destroyButtonTooltip) if self._isDAAPIInited() else None
