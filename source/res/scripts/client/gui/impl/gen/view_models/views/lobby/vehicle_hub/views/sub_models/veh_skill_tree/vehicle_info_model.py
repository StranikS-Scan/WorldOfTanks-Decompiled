# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/views/sub_models/veh_skill_tree/vehicle_info_model.py
from frameworks.wulf import ViewModel

class VehicleInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(VehicleInfoModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def getIsPremium(self):
        return self._getBool(3)

    def setIsPremium(self, value):
        self._setBool(3, value)

    def getPrestigeLevel(self):
        return self._getNumber(4)

    def setPrestigeLevel(self, value):
        self._setNumber(4, value)

    def getIsBroken(self):
        return self._getBool(5)

    def setIsBroken(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(VehicleInfoModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addStringProperty('type', '')
        self._addStringProperty('name', '')
        self._addBoolProperty('isPremium', False)
        self._addNumberProperty('prestigeLevel', 0)
        self._addBoolProperty('isBroken', False)
