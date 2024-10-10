# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/premium_bonuses_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.postbattle.currency_model import CurrencyModel

class PremiumBonusesModel(ViewModel):
    __slots__ = ('onBuyPremium',)

    def __init__(self, properties=1, commands=1):
        super(PremiumBonusesModel, self).__init__(properties=properties, commands=commands)

    def getCurrencies(self):
        return self._getArray(0)

    def setCurrencies(self, value):
        self._setArray(0, value)

    @staticmethod
    def getCurrenciesType():
        return CurrencyModel

    def _initialize(self):
        super(PremiumBonusesModel, self)._initialize()
        self._addArrayProperty('currencies', Array())
        self.onBuyPremium = self._addCommand('onBuyPremium')
