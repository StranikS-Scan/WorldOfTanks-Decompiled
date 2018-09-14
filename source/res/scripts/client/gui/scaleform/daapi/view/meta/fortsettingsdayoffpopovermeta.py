# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortSettingsDayoffPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class FortSettingsDayoffPopoverMeta(SmartPopOverView):

    def onApply(self, dayOff):
        self._printOverrideError('onApply')

    def as_setDescriptionsTextS(self, descriptionText, dayOffText):
        if self._isDAAPIInited():
            return self.flashObject.as_setDescriptionsText(descriptionText, dayOffText)

    def as_setButtonsTextS(self, applyButtonText, cancelButtonText):
        if self._isDAAPIInited():
            return self.flashObject.as_setButtonsText(applyButtonText, cancelButtonText)

    def as_setButtonsTooltipsS(self, enabledApplyButtonTooltip, disabledApplyButtonTooltip):
        if self._isDAAPIInited():
            return self.flashObject.as_setButtonsTooltips(enabledApplyButtonTooltip, disabledApplyButtonTooltip)

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
