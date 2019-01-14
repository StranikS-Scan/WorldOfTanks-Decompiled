# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CustomizationKitPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class CustomizationKitPopoverMeta(SmartPopOverView):

    def removeCustomizationKit(self):
        self._printOverrideError('removeCustomizationKit')

    def updateAutoProlongation(self):
        self._printOverrideError('updateAutoProlongation')

    def as_setHeaderS(self, title):
        return self.flashObject.as_setHeader(title) if self._isDAAPIInited() else None

    def as_getDPS(self):
        return self.flashObject.as_getDP() if self._isDAAPIInited() else None

    def as_showClearMessageS(self, isClear, message):
        return self.flashObject.as_showClearMessage(isClear, message) if self._isDAAPIInited() else None

    def as_setAutoProlongationCheckboxSelectedS(self, value):
        return self.flashObject.as_setAutoProlongationCheckboxSelected(value) if self._isDAAPIInited() else None

    def as_setAutoProlongationCheckboxEnabledS(self, value):
        return self.flashObject.as_setAutoProlongationCheckboxEnabled(value) if self._isDAAPIInited() else None
