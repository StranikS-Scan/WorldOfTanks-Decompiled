# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortSettingsDayoffPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class FortSettingsDayoffPopoverMeta(SmartPopOverView):

    def onApply(self, dayOff):
        self._printOverrideError('onApply')

    def as_setDescriptionsTextS(self, descriptionText, dayOffText):
        return self.flashObject.as_setDescriptionsText(descriptionText, dayOffText) if self._isDAAPIInited() else None

    def as_setButtonsTextS(self, applyButtonText, cancelButtonText):
        return self.flashObject.as_setButtonsText(applyButtonText, cancelButtonText) if self._isDAAPIInited() else None

    def as_setButtonsTooltipsS(self, enabledApplyButtonTooltip, disabledApplyButtonTooltip):
        return self.flashObject.as_setButtonsTooltips(enabledApplyButtonTooltip, disabledApplyButtonTooltip) if self._isDAAPIInited() else None

    def as_setDataS(self, data):
        """
        :param data: Represented by DayOffPopoverVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
