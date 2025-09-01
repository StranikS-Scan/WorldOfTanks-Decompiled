# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/header/wallet_model.py
from frameworks.wulf import Map, ViewModel
from gui.impl.gen.view_models.views.lobby.page.header.currency_model import CurrencyModel

class WalletModel(ViewModel):
    __slots__ = ('onCurrencyAction',)

    def __init__(self, properties=1, commands=1):
        super(WalletModel, self).__init__(properties=properties, commands=commands)

    def getCurrencies(self):
        return self._getMap(0)

    def setCurrencies(self, value):
        self._setMap(0, value)

    @staticmethod
    def getCurrenciesType():
        return (unicode, CurrencyModel)

    def _initialize(self):
        super(WalletModel, self)._initialize()
        self._addMapProperty('currencies', Map(unicode, CurrencyModel))
        self.onCurrencyAction = self._addCommand('onCurrencyAction')
