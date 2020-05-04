# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehiclePreviewSecretEventBuyingActionPanelMeta.py
from gui.Scaleform.daapi.view.lobby.vehiclePreview20.info.vehicle_preview_secret_event_buying_panel import VehiclePreviewSecretEventBuyingPanel

class VehiclePreviewSecretEventBuyingActionPanelMeta(VehiclePreviewSecretEventBuyingPanel):

    def onActionClick(self):
        self._printOverrideError('onActionClick')

    def as_setActionDataS(self, data):
        return self.flashObject.as_setActionData(data) if self._isDAAPIInited() else None
