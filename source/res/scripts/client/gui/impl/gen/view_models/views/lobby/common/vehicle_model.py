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
    PREMIUM_TAG = 'premium'
    SPECIAL = 'special'
    EARN_CRYSTALS = 'earn_crystals'
    PREMIUM_IGR_TAG = 'premiumIGR'
    WOT_PLUS_TAG = 'wotPlus'
    COLLECTOR_VEHICLES_TAG = 'collectorVehicle'

    def __init__(self, properties=10, commands=0):
        super(VehicleModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getLongName(self):
        return self._getString(1)

    def setLongName(self, value):
        self._setString(1, value)

    def getTechName(self):
        return self._getString(2)

    def setTechName(self, value):
        self._setString(2, value)

    def getTier(self):
        return self._getNumber(3)

    def setTier(self, value):
        self._setNumber(3, value)

    def getType(self):
        return self._getString(4)

    def setType(self, value):
        self._setString(4, value)

    def getIsPremium(self):
        return self._getBool(5)

    def setIsPremium(self, value):
        self._setBool(5, value)

    def getTags(self):
        return self._getString(6)

    def setTags(self, value):
        self._setString(6, value)

    def getNation(self):
        return self._getString(7)

    def setNation(self, value):
        self._setString(7, value)

    def getRoleKey(self):
        return self._getString(8)

    def setRoleKey(self, value):
        self._setString(8, value)

    def getVehicleCD(self):
        return self._getNumber(9)

    def setVehicleCD(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(VehicleModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('longName', '')
        self._addStringProperty('techName', '')
        self._addNumberProperty('tier', 0)
        self._addStringProperty('type', '')
        self._addBoolProperty('isPremium', False)
        self._addStringProperty('tags', '')
        self._addStringProperty('nation', '')
        self._addStringProperty('roleKey', '')
        self._addNumberProperty('vehicleCD', 0)
