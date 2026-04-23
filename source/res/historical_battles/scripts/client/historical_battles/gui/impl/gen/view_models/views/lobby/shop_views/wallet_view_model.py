# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/shop_views/wallet_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.money_item_view_model import MoneyItemViewModel

class WalletViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(WalletViewModel, self).__init__(properties=properties, commands=commands)

    def getMoney(self):
        return self._getArray(0)

    def setMoney(self, value):
        self._setArray(0, value)

    @staticmethod
    def getMoneyType():
        return MoneyItemViewModel

    def _initialize(self):
        super(WalletViewModel, self)._initialize()
        self._addArrayProperty('money', Array())
