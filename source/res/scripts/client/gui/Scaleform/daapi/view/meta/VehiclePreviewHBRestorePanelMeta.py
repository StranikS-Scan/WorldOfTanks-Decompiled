# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehiclePreviewHBRestorePanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class VehiclePreviewHBRestorePanelMeta(BaseDAAPIComponent):

    def onBuyClick(self):
        self._printOverrideError('onBuyClick')

    def as_setBuyDataS(self, data):
        return self.flashObject.as_setBuyData(data) if self._isDAAPIInited() else None
