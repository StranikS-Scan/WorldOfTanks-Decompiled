# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/footer/vehicle_compare_model.py
from frameworks.wulf import ViewModel

class VehicleCompareModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(VehicleCompareModel, self).__init__(properties=properties, commands=commands)

    def getVehicleCount(self):
        return self._getNumber(0)

    def setVehicleCount(self, value):
        self._setNumber(0, value)

    def getIsEnabled(self):
        return self._getBool(1)

    def setIsEnabled(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(VehicleCompareModel, self)._initialize()
        self._addNumberProperty('vehicleCount', 0)
        self._addBoolProperty('isEnabled', False)
