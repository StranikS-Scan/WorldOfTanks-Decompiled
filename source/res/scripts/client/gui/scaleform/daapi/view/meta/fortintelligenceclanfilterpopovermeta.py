# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortIntelligenceClanFilterPopoverMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortIntelligenceClanFilterPopoverMeta(DAAPIModule):

    def useFilter(self, value, isDefaultData):
        self._printOverrideError('useFilter')

    def getAvailabilityProvider(self):
        self._printOverrideError('getAvailabilityProvider')

    def as_setDescriptionsTextS(self, header, clanLevel, startHourRange):
        if self._isDAAPIInited():
            return self.flashObject.as_setDescriptionsText(header, clanLevel, startHourRange)

    def as_setButtonsTextS(self, defaultButtonText, applyButtonText, cancelButtonText):
        if self._isDAAPIInited():
            return self.flashObject.as_setButtonsText(defaultButtonText, applyButtonText, cancelButtonText)

    def as_setButtonsTooltipsS(self, defaultButtonTooltip, applyButtonTooltip):
        if self._isDAAPIInited():
            return self.flashObject.as_setButtonsTooltips(defaultButtonTooltip, applyButtonTooltip)

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
