# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortIntelligenceClanFilterPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class FortIntelligenceClanFilterPopoverMeta(SmartPopOverView):

    def useFilter(self, value, isDefaultData):
        self._printOverrideError('useFilter')

    def getAvailabilityProvider(self):
        self._printOverrideError('getAvailabilityProvider')

    def as_setDescriptionsTextS(self, header, clanLevel, startHourRange):
        return self.flashObject.as_setDescriptionsText(header, clanLevel, startHourRange) if self._isDAAPIInited() else None

    def as_setButtonsTextS(self, defaultButtonText, applyButtonText, cancelButtonText):
        return self.flashObject.as_setButtonsText(defaultButtonText, applyButtonText, cancelButtonText) if self._isDAAPIInited() else None

    def as_setButtonsTooltipsS(self, defaultButtonTooltip, applyButtonTooltip):
        return self.flashObject.as_setButtonsTooltips(defaultButtonTooltip, applyButtonTooltip) if self._isDAAPIInited() else None

    def as_setDataS(self, data):
        """
        :param data: Represented by IntelligenceClanFilterVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
