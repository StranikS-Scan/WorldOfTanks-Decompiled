# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/tooltips/deconstruct_from_vehicle_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class DeconstructFromVehicleTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(DeconstructFromVehicleTooltipModel, self).__init__(properties=properties, commands=commands)

    def getEquipmentName(self):
        return self._getString(0)

    def setEquipmentName(self, value):
        self._setString(0, value)

    def getVehicleNames(self):
        return self._getArray(1)

    def setVehicleNames(self, value):
        self._setArray(1, value)

    @staticmethod
    def getVehicleNamesType():
        return unicode

    def _initialize(self):
        super(DeconstructFromVehicleTooltipModel, self)._initialize()
        self._addStringProperty('equipmentName', '')
        self._addArrayProperty('vehicleNames', Array())
