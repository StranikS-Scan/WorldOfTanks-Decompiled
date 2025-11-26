# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tooltips/earnings_model.py
from frameworks.wulf import Array, ViewModel

class EarningsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
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

    def getTelecomRent(self):
        return self._getBool(5)

    def setTelecomRent(self, value):
        self._setBool(5, value)

    def getTradeIn(self):
        return self._getBool(6)

    def setTradeIn(self, value):
        self._setBool(6, value)

    def getNumberOfCrystalEarned(self):
        return self._getArray(7)

    def setNumberOfCrystalEarned(self, value):
        self._setArray(7, value)

    @staticmethod
    def getNumberOfCrystalEarnedType():
        return int

    def getCurrentBpScore(self):
        return self._getNumber(8)

    def setCurrentBpScore(self, value):
        self._setNumber(8, value)

    def getWotPlusExpiryTime(self):
        return self._getNumber(9)

    def setWotPlusExpiryTime(self, value):
        self._setNumber(9, value)

    def getWotPlusState(self):
        return self._getString(10)

    def setWotPlusState(self, value):
        self._setString(10, value)

    def getMaxBpScore(self):
        return self._getNumber(11)

    def setMaxBpScore(self, value):
        self._setNumber(11, value)

    def getBpReward(self):
        return self._getNumber(12)

    def setBpReward(self, value):
        self._setNumber(12, value)

    def getBpActive(self):
        return self._getBool(13)

    def setBpActive(self, value):
        self._setBool(13, value)

    def _initialize(self):
        super(EarningsModel, self)._initialize()
        self._addNumberProperty('xp', 0)
        self._addNumberProperty('bonusMultiplier', -1)
        self._addBoolProperty('crystalEarning', False)
        self._addNumberProperty('crystalTimeout', 0)
        self._addBoolProperty('wotPlus', False)
        self._addBoolProperty('telecomRent', False)
        self._addBoolProperty('tradeIn', False)
        self._addArrayProperty('numberOfCrystalEarned', Array())
        self._addNumberProperty('currentBpScore', -1)
        self._addNumberProperty('wotPlusExpiryTime', 0)
        self._addStringProperty('wotPlusState', '')
        self._addNumberProperty('maxBpScore', -1)
        self._addNumberProperty('bpReward', 0)
        self._addBoolProperty('bpActive', False)
