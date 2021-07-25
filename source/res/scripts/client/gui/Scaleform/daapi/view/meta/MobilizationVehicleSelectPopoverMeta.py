# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MobilizationVehicleSelectPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.vehicle_select_popover_base import VehicleSelectPopoverBase

class MobilizationVehicleSelectPopoverMeta(VehicleSelectPopoverBase):

    def onSearchInputChange(self, inputText):
        self._printOverrideError('onSearchInputChange')

    def onResetButtonClick(self):
        self._printOverrideError('onResetButtonClick')

    def as_updateFilterStatusS(self, data):
        return self.flashObject.as_updateFilterStatus(data) if self._isDAAPIInited() else None
