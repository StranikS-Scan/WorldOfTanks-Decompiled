# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/vehicle_model.py
from frameworks.wulf import ViewModel

class VehicleModel(ViewModel):
    __slots__ = ()
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
    LIGHT_TANK = 'lightTank'
    MEDIUM_TANK = 'mediumTank'
    HEAVY_TANK = 'heavyTank'
    SPG = 'SPG'
    AT_SPG = 'AT-SPG'

    def __init__(self, properties=7, commands=0):
        super(VehicleModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getTechName(self):
        return self._getString(1)

    def setTechName(self, value):
        self._setString(1, value)

    def getTier(self):
        return self._getNumber(2)

    def setTier(self, value):
        self._setNumber(2, value)

    def getType(self):
        return self._getString(3)

    def setType(self, value):
        self._setString(3, value)

    def getIsPremium(self):
        return self._getBool(4)

    def setIsPremium(self, value):
        self._setBool(4, value)

    def getNation(self):
        return self._getString(5)

    def setNation(self, value):
        self._setString(5, value)

    def getVehicleCD(self):
        return self._getNumber(6)

    def setVehicleCD(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(VehicleModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('techName', '')
        self._addNumberProperty('tier', 0)
        self._addStringProperty('type', '')
        self._addBoolProperty('isPremium', False)
        self._addStringProperty('nation', '')
        self._addNumberProperty('vehicleCD', 0)
