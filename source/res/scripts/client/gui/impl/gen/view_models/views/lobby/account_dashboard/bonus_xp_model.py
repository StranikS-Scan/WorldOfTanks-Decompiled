# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_dashboard/bonus_xp_model.py
from frameworks.wulf import ViewModel

class BonusXpModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=8, commands=1):
        super(BonusXpModel, self).__init__(properties=properties, commands=commands)

    def getIsEnabled(self):
        return self._getBool(0)

    def setIsEnabled(self, value):
        self._setBool(0, value)

    def getMultiplier(self):
        return self._getNumber(1)

    def setMultiplier(self, value):
        self._setNumber(1, value)

    def getTotalUses(self):
        return self._getNumber(2)

    def setTotalUses(self, value):
        self._setNumber(2, value)

    def getUsesLeft(self):
        return self._getNumber(3)

    def setUsesLeft(self, value):
        self._setNumber(3, value)

    def getIsWotPlusBonusEnabled(self):
        return self._getBool(4)

    def setIsWotPlusBonusEnabled(self, value):
        self._setBool(4, value)

    def getIsWotPremium(self):
        return self._getBool(5)

    def setIsWotPremium(self, value):
        self._setBool(5, value)

    def getIsWotPlus(self):
        return self._getBool(6)

    def setIsWotPlus(self, value):
        self._setBool(6, value)

    def getDailyAppliedXP(self):
        return self._getNumber(7)

    def setDailyAppliedXP(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(BonusXpModel, self)._initialize()
        self._addBoolProperty('isEnabled', True)
        self._addNumberProperty('multiplier', 1)
        self._addNumberProperty('totalUses', 0)
        self._addNumberProperty('usesLeft', 0)
        self._addBoolProperty('isWotPlusBonusEnabled', False)
        self._addBoolProperty('isWotPremium', False)
        self._addBoolProperty('isWotPlus', False)
        self._addNumberProperty('dailyAppliedXP', 0)
        self.onClick = self._addCommand('onClick')
