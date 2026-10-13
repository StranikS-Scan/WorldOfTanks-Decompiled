# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/comparison_vehicle_model.py
from frameworks.wulf import ViewModel

class ComparisonVehicleModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(ComparisonVehicleModel, self).__init__(properties=properties, commands=commands)

    def getVehicleName(self):
        return self._getString(0)

    def setVehicleName(self, value):
        self._setString(0, value)

    def getVehicleType(self):
        return self._getString(1)

    def setVehicleType(self, value):
        self._setString(1, value)

    def getUserName(self):
        return self._getString(2)

    def setUserName(self, value):
        self._setString(2, value)

    def getRelativePower(self):
        return self._getNumber(3)

    def setRelativePower(self, value):
        self._setNumber(3, value)

    def getSpeedLimit(self):
        return self._getNumber(4)

    def setSpeedLimit(self, value):
        self._setNumber(4, value)

    def getMaxHealth(self):
        return self._getNumber(5)

    def setMaxHealth(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(ComparisonVehicleModel, self)._initialize()
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('userName', '')
        self._addNumberProperty('relativePower', 0)
        self._addNumberProperty('speedLimit', 0)
        self._addNumberProperty('maxHealth', 0)
