# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/exchange/currency_tab_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.exchange.currency_model import CurrencyModel

class CurrencyTabModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(CurrencyTabModel, self).__init__(properties=properties, commands=commands)

    def getCurrencies(self):
        return self._getArray(0)

    def setCurrencies(self, value):
        self._setArray(0, value)

    @staticmethod
    def getCurrenciesType():
        return CurrencyModel

    def getIsWalletAvailable(self):
        return self._getBool(1)

    def setIsWalletAvailable(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(CurrencyTabModel, self)._initialize()
        self._addArrayProperty('currencies', Array())
        self._addBoolProperty('isWalletAvailable', True)
