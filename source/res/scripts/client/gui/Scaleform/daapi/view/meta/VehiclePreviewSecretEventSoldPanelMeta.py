# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehiclePreviewSecretEventSoldPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class VehiclePreviewSecretEventSoldPanelMeta(BaseDAAPIComponent):

    def onRestoreClick(self):
        self._printOverrideError('onRestoreClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
