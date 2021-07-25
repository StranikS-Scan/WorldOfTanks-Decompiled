# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/vehicle_model.py
from frameworks.wulf import ViewModel

class VehicleModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(VehicleModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getLevel(self):
        return self._getNumber(3)

    def setLevel(self, value):
        self._setNumber(3, value)

    def getType(self):
        return self._getString(4)

    def setType(self, value):
        self._setString(4, value)

    def getNation(self):
        return self._getString(5)

    def setNation(self, value):
        self._setString(5, value)

    def getIsElite(self):
        return self._getBool(6)

    def setIsElite(self, value):
        self._setBool(6, value)

    def getIsPremium(self):
        return self._getBool(7)

    def setIsPremium(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(VehicleModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('icon', '')
        self._addNumberProperty('level', 0)
        self._addStringProperty('type', '')
        self._addStringProperty('nation', '')
        self._addBoolProperty('isElite', False)
        self._addBoolProperty('isPremium', False)
