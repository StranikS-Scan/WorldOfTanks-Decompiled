# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_dashboard/premium_account_model.py
from frameworks.wulf import ViewModel

class PremiumAccountModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=10, commands=1):
        super(PremiumAccountModel, self).__init__(properties=properties, commands=commands)

    def getIsEnabled(self):
        return self._getBool(0)

    def setIsEnabled(self, value):
        self._setBool(0, value)

    def getWotPremiumSecondsLeft(self):
        return self._getNumber(1)

    def setWotPremiumSecondsLeft(self, value):
        self._setNumber(1, value)

    def getWgPremiumSecondsLeft(self):
        return self._getNumber(2)

    def setWgPremiumSecondsLeft(self, value):
        self._setNumber(2, value)

    def getXpBonus(self):
        return self._getNumber(3)

    def setXpBonus(self, value):
        self._setNumber(3, value)

    def getCreditBonus(self):
        return self._getNumber(4)

    def setCreditBonus(self, value):
        self._setNumber(4, value)

    def getPlatoonBonus(self):
        return self._getNumber(5)

    def setPlatoonBonus(self, value):
        self._setNumber(5, value)

    def getStandardAccountCredits(self):
        return self._getNumber(6)

    def setStandardAccountCredits(self, value):
        self._setNumber(6, value)

    def getStandardAccountXp(self):
        return self._getNumber(7)

    def setStandardAccountXp(self, value):
        self._setNumber(7, value)

    def getPremiumAccountCredits(self):
        return self._getNumber(8)

    def setPremiumAccountCredits(self, value):
        self._setNumber(8, value)

    def getPremiumAccountXp(self):
        return self._getNumber(9)

    def setPremiumAccountXp(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(PremiumAccountModel, self)._initialize()
        self._addBoolProperty('isEnabled', True)
        self._addNumberProperty('wotPremiumSecondsLeft', 0)
        self._addNumberProperty('wgPremiumSecondsLeft', 0)
        self._addNumberProperty('xpBonus', 50)
        self._addNumberProperty('creditBonus', 50)
        self._addNumberProperty('platoonBonus', 15)
        self._addNumberProperty('standardAccountCredits', 0)
        self._addNumberProperty('standardAccountXp', 0)
        self._addNumberProperty('premiumAccountCredits', 0)
        self._addNumberProperty('premiumAccountXp', 0)
        self.onClick = self._addCommand('onClick')
