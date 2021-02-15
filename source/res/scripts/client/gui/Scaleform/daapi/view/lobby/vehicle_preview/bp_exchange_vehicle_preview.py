# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/bp_exchange_vehicle_preview.py
from gui.Scaleform.daapi.view.lobby.vehicle_preview.style_preview import VehicleStylePreview

class BlueprintsExchangeVehicleStypePreview(VehicleStylePreview):

    def onBackClick(self):
        self.closeView()
        super(BlueprintsExchangeVehicleStypePreview, self).onBackClick()
