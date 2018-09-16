# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CustomizationStyleAnchorPropertiesMeta.py
from gui.Scaleform.daapi.view.lobby.customization.anchor_properties import AnchorProperties

class CustomizationStyleAnchorPropertiesMeta(AnchorProperties):

    def showRemoveConfirmation(self):
        self._printOverrideError('showRemoveConfirmation')

    def autoProlongationSwitch(self, select):
        self._printOverrideError('autoProlongationSwitch')

    def as_setPopoverDataS(self, data):
        return self.flashObject.as_setPopoverData(data) if self._isDAAPIInited() else None
