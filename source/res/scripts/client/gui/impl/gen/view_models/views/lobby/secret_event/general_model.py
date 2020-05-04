# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/general_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class GeneralModel(ViewModel):
    __slots__ = ()
    LEVEL_1 = '1'
    LEVEL_2 = '2'
    LEVEL_3 = '3'
    LIGHT_TANK = 'lightTank'
    MEDIUM_TANK = 'mediumTank'
    HEAVY_TANK = 'heavyTank'
    SPG = 'SPG'
    AT_SPG = 'AT-SPG'

    def __init__(self, properties=11, commands=0):
        super(GeneralModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getLabel(self):
        return self._getResource(1)

    def setLabel(self, value):
        self._setResource(1, value)

    def getLevel(self):
        return self._getString(2)

    def setLevel(self, value):
        self._setString(2, value)

    def getIsSelected(self):
        return self._getBool(3)

    def setIsSelected(self, value):
        self._setBool(3, value)

    def getIsInBattle(self):
        return self._getBool(4)

    def setIsInBattle(self, value):
        self._setBool(4, value)

    def getIsInPlatoon(self):
        return self._getBool(5)

    def setIsInPlatoon(self, value):
        self._setBool(5, value)

    def getOrderLabel(self):
        return self._getString(6)

    def setOrderLabel(self, value):
        self._setString(6, value)

    def getCurrentProgress(self):
        return self._getNumber(7)

    def setCurrentProgress(self, value):
        self._setNumber(7, value)

    def getMaxProgress(self):
        return self._getNumber(8)

    def setMaxProgress(self, value):
        self._setNumber(8, value)

    def getVehicleType(self):
        return self._getString(9)

    def setVehicleType(self, value):
        self._setString(9, value)

    def getVehicleIcon(self):
        return self._getResource(10)

    def setVehicleIcon(self, value):
        self._setResource(10, value)

    def _initialize(self):
        super(GeneralModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addResourceProperty('label', R.invalid())
        self._addStringProperty('level', '')
        self._addBoolProperty('isSelected', False)
        self._addBoolProperty('isInBattle', False)
        self._addBoolProperty('isInPlatoon', False)
        self._addStringProperty('orderLabel', '')
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('maxProgress', 0)
        self._addStringProperty('vehicleType', '')
        self._addResourceProperty('vehicleIcon', R.invalid())
