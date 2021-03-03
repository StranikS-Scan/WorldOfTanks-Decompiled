# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/vehicle_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class VehicleType(Enum):
    HEAVY = 'heavyTank'
    MEDIUM = 'mediumTank'
    LIGHT = 'lightTank'
    SPG = 'SPG'
    ATSPG = 'AT-SPG'


class NationType(Enum):
    USSR = 'ussr'
    GERMANY = 'germany'
    USA = 'usa'
    CHINA = 'china'
    FRANCE = 'france'
    UK = 'uk'
    JAPAN = 'japan'
    CZECH = 'czech'
    SWEDEN = 'sweden'
    POLAND = 'poland'
    ITALY = 'italy'


class VehicleModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(VehicleModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getType(self):
        return VehicleType(self._getString(1))

    def setType(self, value):
        self._setString(1, value.value)

    def getNation(self):
        return NationType(self._getString(2))

    def setNation(self, value):
        self._setString(2, value.value)

    def getLevel(self):
        return self._getNumber(3)

    def setLevel(self, value):
        self._setNumber(3, value)

    def getTooltipId(self):
        return self._getNumber(4)

    def setTooltipId(self, value):
        self._setNumber(4, value)

    def getVehicleId(self):
        return self._getNumber(5)

    def setVehicleId(self, value):
        self._setNumber(5, value)

    def getVehicleTechName(self):
        return self._getString(6)

    def setVehicleTechName(self, value):
        self._setString(6, value)

    def getImageName(self):
        return self._getString(7)

    def setImageName(self, value):
        self._setString(7, value)

    def getIsPremium(self):
        return self._getBool(8)

    def setIsPremium(self, value):
        self._setBool(8, value)

    def getIsFromStorage(self):
        return self._getBool(9)

    def setIsFromStorage(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(VehicleModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('type')
        self._addStringProperty('nation')
        self._addNumberProperty('level', 0)
        self._addNumberProperty('tooltipId', 0)
        self._addNumberProperty('vehicleId', 0)
        self._addStringProperty('vehicleTechName', '')
        self._addStringProperty('imageName', '')
        self._addBoolProperty('isPremium', True)
        self._addBoolProperty('isFromStorage', False)
