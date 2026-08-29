# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/portal_rewards/wt_currency_balance_model.py
from frameworks.wulf import ViewModel

class WtCurrencyBalanceModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(WtCurrencyBalanceModel, self).__init__(properties=properties, commands=commands)

    def getIsWalletAvailable(self):
        return self._getBool(0)

    def setIsWalletAvailable(self, value):
        self._setBool(0, value)

    def getCrystal(self):
        return self._getNumber(1)

    def setCrystal(self, value):
        self._setNumber(1, value)

    def getGold(self):
        return self._getNumber(2)

    def setGold(self, value):
        self._setNumber(2, value)

    def getCredits(self):
        return self._getNumber(3)

    def setCredits(self, value):
        self._setNumber(3, value)

    def getFreeXp(self):
        return self._getNumber(4)

    def setFreeXp(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(WtCurrencyBalanceModel, self)._initialize()
        self._addBoolProperty('isWalletAvailable', False)
        self._addNumberProperty('crystal', 0)
        self._addNumberProperty('gold', 0)
        self._addNumberProperty('credits', 0)
        self._addNumberProperty('freeXp', 0)
