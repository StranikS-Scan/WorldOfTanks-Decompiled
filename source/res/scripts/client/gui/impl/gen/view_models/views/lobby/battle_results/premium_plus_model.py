# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/premium_plus_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class PremiumXpBonusRestriction(IntEnum):
    NORESTRICTION = 0
    ISAPPLIED = 1
    INVALIDBATTLETYPE = 2
    ISNOTVICTORY = 3
    DEPRECATEDRESULTS = 4
    NOVEHICLE = 5
    NOCREW = 6
    FASTEREDUCATIONCREWNOTACTIVE = 7
    FASTEREDUCATIONCREWACTIVE = 8
    NOTAPPLYINGERROR = 9


class PremiumPlusModel(ViewModel):
    __slots__ = ('onPremiumXpBonusApplied',)

    def __init__(self, properties=9, commands=1):
        super(PremiumPlusModel, self).__init__(properties=properties, commands=commands)

    def getHasPremium(self):
        return self._getBool(0)

    def setHasPremium(self, value):
        self._setBool(0, value)

    def getWasPremium(self):
        return self._getBool(1)

    def setWasPremium(self, value):
        self._setBool(1, value)

    def getIsXpBonusEnabled(self):
        return self._getBool(2)

    def setIsXpBonusEnabled(self, value):
        self._setBool(2, value)

    def getBonusMultiplier(self):
        return self._getNumber(3)

    def setBonusMultiplier(self, value):
        self._setNumber(3, value)

    def getXpDiff(self):
        return self._getNumber(4)

    def setXpDiff(self, value):
        self._setNumber(4, value)

    def getLeftBonusCount(self):
        return self._getNumber(5)

    def setLeftBonusCount(self, value):
        self._setNumber(5, value)

    def getIsUndefinedLeftBonusCount(self):
        return self._getBool(6)

    def setIsUndefinedLeftBonusCount(self, value):
        self._setBool(6, value)

    def getNextBonusTime(self):
        return self._getReal(7)

    def setNextBonusTime(self, value):
        self._setReal(7, value)

    def getRestriction(self):
        return PremiumXpBonusRestriction(self._getNumber(8))

    def setRestriction(self, value):
        self._setNumber(8, value.value)

    def _initialize(self):
        super(PremiumPlusModel, self)._initialize()
        self._addBoolProperty('hasPremium', False)
        self._addBoolProperty('wasPremium', False)
        self._addBoolProperty('isXpBonusEnabled', False)
        self._addNumberProperty('bonusMultiplier', 0)
        self._addNumberProperty('xpDiff', 0)
        self._addNumberProperty('leftBonusCount', 0)
        self._addBoolProperty('isUndefinedLeftBonusCount', False)
        self._addRealProperty('nextBonusTime', -1)
        self._addNumberProperty('restriction', PremiumXpBonusRestriction.NORESTRICTION.value)
        self.onPremiumXpBonusApplied = self._addCommand('onPremiumXpBonusApplied')
