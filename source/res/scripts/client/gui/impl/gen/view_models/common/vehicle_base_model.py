# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/vehicle_base_model.py
from enum import Enum
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class VehicleNation(Enum):
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


class VehicleClass(Enum):
    LIGHTTANK = 'lightTank'
    MEDIUMTANK = 'mediumTank'
    HEAVYTANK = 'heavyTank'
    AT_SPG = 'AT_SPG'
    SPG = 'SPG'


class VehicleBaseModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(VehicleBaseModel, self).__init__(properties=properties, commands=commands)

    def getIntCD(self):
        return self._getNumber(0)

    def setIntCD(self, value):
        self._setNumber(0, value)

    def getNation(self):
        return VehicleNation(self._getString(1))

    def setNation(self, value):
        self._setString(1, value.value)

    def getClass(self):
        return VehicleClass(self._getString(2))

    def setClass(self, value):
        self._setString(2, value.value)

    def getTier(self):
        return self._getNumber(3)

    def setTier(self, value):
        self._setNumber(3, value)

    def getShortName(self):
        return self._getString(4)

    def setShortName(self, value):
        self._setString(4, value)

    def getIsElite(self):
        return self._getBool(5)

    def setIsElite(self, value):
        self._setBool(5, value)

    def getIsPremium(self):
        return self._getBool(6)

    def setIsPremium(self, value):
        self._setBool(6, value)

    def getImage(self):
        return self._getResource(7)

    def setImage(self, value):
        self._setResource(7, value)

    def _initialize(self):
        super(VehicleBaseModel, self)._initialize()
        self._addNumberProperty('intCD', 0)
        self._addStringProperty('nation')
        self._addStringProperty('class')
        self._addNumberProperty('tier', 1)
        self._addStringProperty('shortName', '')
        self._addBoolProperty('isElite', False)
        self._addBoolProperty('isPremium', False)
        self._addResourceProperty('image', R.invalid())
