# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehiclePreviewHBPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class VehiclePreviewHBPanelMeta(BaseDAAPIComponent):

    def onAcceptClicked(self):
        self._printOverrideError('onAcceptClicked')

    def onSecondaryClicked(self):
        self._printOverrideError('onSecondaryClicked')

    def showTooltip(self, intCD, itemType):
        self._printOverrideError('showTooltip')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
