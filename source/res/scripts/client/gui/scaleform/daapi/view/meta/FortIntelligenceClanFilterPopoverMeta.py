# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortIntelligenceClanFilterPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class FortIntelligenceClanFilterPopoverMeta(SmartPopOverView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends SmartPopOverView
    null
    """

    def useFilter(self, value, isDefaultData):
        """
        :param value:
        :param isDefaultData:
        :return :
        """
        self._printOverrideError('useFilter')

    def getAvailabilityProvider(self):
        """
        :return Array:
        """
        self._printOverrideError('getAvailabilityProvider')

    def as_setDescriptionsTextS(self, header, clanLevel, startHourRange):
        """
        :param header:
        :param clanLevel:
        :param startHourRange:
        :return :
        """
        return self.flashObject.as_setDescriptionsText(header, clanLevel, startHourRange) if self._isDAAPIInited() else None

    def as_setButtonsTextS(self, defaultButtonText, applyButtonText, cancelButtonText):
        """
        :param defaultButtonText:
        :param applyButtonText:
        :param cancelButtonText:
        :return :
        """
        return self.flashObject.as_setButtonsText(defaultButtonText, applyButtonText, cancelButtonText) if self._isDAAPIInited() else None

    def as_setButtonsTooltipsS(self, defaultButtonTooltip, applyButtonTooltip):
        """
        :param defaultButtonTooltip:
        :param applyButtonTooltip:
        :return :
        """
        return self.flashObject.as_setButtonsTooltips(defaultButtonTooltip, applyButtonTooltip) if self._isDAAPIInited() else None

    def as_setDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
