# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/vehicle_title_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class VehicleTypes(Enum):
    NONE = 'none'
    LIGHTTANK = 'lightTank'
    MEDIUMTANK = 'mediumTank'
    HEAVYTANK = 'heavyTank'
    SPG = 'SPG'
    AT_SPG = 'AT-SPG'


class VehicleTitleViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(VehicleTitleViewModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getLevel(self):
        return self._getNumber(2)

    def setLevel(self, value):
        self._setNumber(2, value)

    def getRole(self):
        return self._getNumber(3)

    def setRole(self, value):
        self._setNumber(3, value)

    def getNation(self):
        return self._getString(4)

    def setNation(self, value):
        self._setString(4, value)

    def getIsPremium(self):
        return self._getBool(5)

    def setIsPremium(self, value):
        self._setBool(5, value)

    def getVehicleType(self):
        return VehicleTypes(self._getString(6))

    def setVehicleType(self, value):
        self._setString(6, value.value)

    def _initialize(self):
        super(VehicleTitleViewModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('name', '')
        self._addNumberProperty('level', 0)
        self._addNumberProperty('role', 0)
        self._addStringProperty('nation', '')
        self._addBoolProperty('isPremium', False)
        self._addStringProperty('vehicleType')
