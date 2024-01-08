# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/bonuses/compensation_bonus_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class VehicleType(Enum):
    HEAVY = 'heavyTank'
    MEDIUM = 'mediumTank'
    LIGHT = 'lightTank'
    SPG = 'SPG'
    ATSPG = 'AT-SPG'


class CompensationBonusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(CompensationBonusModel, self).__init__(properties=properties, commands=commands)

    def getIndex(self):
        return self._getNumber(0)

    def setIndex(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getValue(self):
        return self._getString(2)

    def setValue(self, value):
        self._setString(2, value)

    def getIsCompensation(self):
        return self._getBool(3)

    def setIsCompensation(self, value):
        self._setBool(3, value)

    def getIcon(self):
        return self._getString(4)

    def setIcon(self, value):
        self._setString(4, value)

    def getVehicleName(self):
        return self._getString(5)

    def setVehicleName(self, value):
        self._setString(5, value)

    def getType(self):
        return VehicleType(self._getString(6))

    def setType(self, value):
        self._setString(6, value.value)

    def getLevel(self):
        return self._getNumber(7)

    def setLevel(self, value):
        self._setNumber(7, value)

    def getLabel(self):
        return self._getString(8)

    def setLabel(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(CompensationBonusModel, self)._initialize()
        self._addNumberProperty('index', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('value', '')
        self._addBoolProperty('isCompensation', False)
        self._addStringProperty('icon', '')
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('type')
        self._addNumberProperty('level', 0)
        self._addStringProperty('label', '')
