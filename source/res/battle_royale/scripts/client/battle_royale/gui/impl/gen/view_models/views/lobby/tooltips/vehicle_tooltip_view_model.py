# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/tooltips/vehicle_tooltip_view_model.py
from frameworks.wulf import ViewModel

class VehicleTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(VehicleTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getVehicleName(self):
        return self._getString(0)

    def setVehicleName(self, value):
        self._setString(0, value)

    def getVehicleNation(self):
        return self._getString(1)

    def setVehicleNation(self, value):
        self._setString(1, value)

    def getStatusLevel(self):
        return self._getString(2)

    def setStatusLevel(self, value):
        self._setString(2, value)

    def getStatusText(self):
        return self._getString(3)

    def setStatusText(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(VehicleTooltipViewModel, self)._initialize()
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleNation', '')
        self._addStringProperty('statusLevel', '')
        self._addStringProperty('statusText', '')
