# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/gen/view_models/views/lobby/tank_academy/tank_academy_vehicle_model.py
from frameworks.wulf import ViewModel

class TankAcademyVehicleModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(TankAcademyVehicleModel, self).__init__(properties=properties, commands=commands)

    def getIsElite(self):
        return self._getBool(0)

    def setIsElite(self, value):
        self._setBool(0, value)

    def getIsPremium(self):
        return self._getBool(1)

    def setIsPremium(self, value):
        self._setBool(1, value)

    def getIsInHangar(self):
        return self._getBool(2)

    def setIsInHangar(self, value):
        self._setBool(2, value)

    def getVehCD(self):
        return self._getNumber(3)

    def setVehCD(self, value):
        self._setNumber(3, value)

    def getRentLength(self):
        return self._getNumber(4)

    def setRentLength(self, value):
        self._setNumber(4, value)

    def getLevel(self):
        return self._getNumber(5)

    def setLevel(self, value):
        self._setNumber(5, value)

    def getVehType(self):
        return self._getString(6)

    def setVehType(self, value):
        self._setString(6, value)

    def getVehName(self):
        return self._getString(7)

    def setVehName(self, value):
        self._setString(7, value)

    def getUserName(self):
        return self._getString(8)

    def setUserName(self, value):
        self._setString(8, value)

    def getNation(self):
        return self._getString(9)

    def setNation(self, value):
        self._setString(9, value)

    def getRoleKey(self):
        return self._getString(10)

    def setRoleKey(self, value):
        self._setString(10, value)

    def getIsBranchContinuation(self):
        return self._getBool(11)

    def setIsBranchContinuation(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(TankAcademyVehicleModel, self)._initialize()
        self._addBoolProperty('isElite', False)
        self._addBoolProperty('isPremium', False)
        self._addBoolProperty('isInHangar', False)
        self._addNumberProperty('vehCD', 0)
        self._addNumberProperty('rentLength', 0)
        self._addNumberProperty('level', 0)
        self._addStringProperty('vehType', '')
        self._addStringProperty('vehName', '')
        self._addStringProperty('userName', '')
        self._addStringProperty('nation', '')
        self._addStringProperty('roleKey', '')
        self._addBoolProperty('isBranchContinuation', False)
