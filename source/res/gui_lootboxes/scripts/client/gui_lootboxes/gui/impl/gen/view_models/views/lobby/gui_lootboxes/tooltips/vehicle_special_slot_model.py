# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/tooltips/vehicle_special_slot_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class VehicleSpecialSlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(VehicleSpecialSlotModel, self).__init__(properties=properties, commands=commands)

    def getProbability(self):
        return self._getReal(0)

    def setProbability(self, value):
        self._setReal(0, value)

    def getGarant(self):
        return self._getNumber(1)

    def setGarant(self, value):
        self._setNumber(1, value)

    def getMaxLevel(self):
        return self._getNumber(2)

    def setMaxLevel(self, value):
        self._setNumber(2, value)

    def getMinLevel(self):
        return self._getNumber(3)

    def setMinLevel(self, value):
        self._setNumber(3, value)

    def getVehicleNames(self):
        return self._getArray(4)

    def setVehicleNames(self, value):
        self._setArray(4, value)

    @staticmethod
    def getVehicleNamesType():
        return unicode

    def getVehicleLevels(self):
        return self._getArray(5)

    def setVehicleLevels(self, value):
        self._setArray(5, value)

    @staticmethod
    def getVehicleLevelsType():
        return int

    def _initialize(self):
        super(VehicleSpecialSlotModel, self)._initialize()
        self._addRealProperty('probability', 0.0)
        self._addNumberProperty('garant', 0)
        self._addNumberProperty('maxLevel', 0)
        self._addNumberProperty('minLevel', 0)
        self._addArrayProperty('vehicleNames', Array())
        self._addArrayProperty('vehicleLevels', Array())
