# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tooltips/earnings_model.py
from frameworks.wulf import Array, ViewModel

class EarningsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(EarningsModel, self).__init__(properties=properties, commands=commands)

    def getXp(self):
        return self._getNumber(0)

    def setXp(self, value):
        self._setNumber(0, value)

    def getBonusMultiplier(self):
        return self._getNumber(1)

    def setBonusMultiplier(self, value):
        self._setNumber(1, value)

    def getCrystalEarning(self):
        return self._getBool(2)

    def setCrystalEarning(self, value):
        self._setBool(2, value)

    def getCrystalTimeout(self):
        return self._getNumber(3)

    def setCrystalTimeout(self, value):
        self._setNumber(3, value)

    def getWotPlus(self):
        return self._getBool(4)

    def setWotPlus(self, value):
        self._setBool(4, value)

    def getNumberOfCrystalEarned(self):
        return self._getArray(5)

    def setNumberOfCrystalEarned(self, value):
        self._setArray(5, value)

    @staticmethod
    def getNumberOfCrystalEarnedType():
        return int

    def getCurrentBpScore(self):
        return self._getNumber(6)

    def setCurrentBpScore(self, value):
        self._setNumber(6, value)

    def getWotPlusExpiryTime(self):
        return self._getNumber(7)

    def setWotPlusExpiryTime(self, value):
        self._setNumber(7, value)

    def getWotPlusState(self):
        return self._getString(8)

    def setWotPlusState(self, value):
        self._setString(8, value)

    def getMaxBpScore(self):
        return self._getNumber(9)

    def setMaxBpScore(self, value):
        self._setNumber(9, value)

    def getBpReward(self):
        return self._getNumber(10)

    def setBpReward(self, value):
        self._setNumber(10, value)

    def getBpActive(self):
        return self._getBool(11)

    def setBpActive(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(EarningsModel, self)._initialize()
        self._addNumberProperty('xp', 0)
        self._addNumberProperty('bonusMultiplier', -1)
        self._addBoolProperty('crystalEarning', False)
        self._addNumberProperty('crystalTimeout', 0)
        self._addBoolProperty('wotPlus', False)
        self._addArrayProperty('numberOfCrystalEarned', Array())
        self._addNumberProperty('currentBpScore', -1)
        self._addNumberProperty('wotPlusExpiryTime', 0)
        self._addStringProperty('wotPlusState', '')
        self._addNumberProperty('maxBpScore', -1)
        self._addNumberProperty('bpReward', 0)
        self._addBoolProperty('bpActive', False)
