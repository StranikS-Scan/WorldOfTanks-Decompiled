# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/lobby/vehicles_carousel/races_vehicle_info_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class RacesVehicleInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(RacesVehicleInfoModel, self).__init__(properties=properties, commands=commands)

    def getVehicleName(self):
        return self._getString(0)

    def setVehicleName(self, value):
        self._setString(0, value)

    def getVehicleUserName(self):
        return self._getString(1)

    def setVehicleUserName(self, value):
        self._setString(1, value)

    def getTooltipName(self):
        return self._getString(2)

    def setTooltipName(self, value):
        self._setString(2, value)

    def getInBattle(self):
        return self._getBool(3)

    def setInBattle(self, value):
        self._setBool(3, value)

    def getVehiclePropertyArray(self):
        return self._getArray(4)

    def setVehiclePropertyArray(self, value):
        self._setArray(4, value)

    @staticmethod
    def getVehiclePropertyArrayType():
        return int

    def _initialize(self):
        super(RacesVehicleInfoModel, self)._initialize()
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleUserName', '')
        self._addStringProperty('tooltipName', '')
        self._addBoolProperty('inBattle', False)
        self._addArrayProperty('vehiclePropertyArray', Array())
