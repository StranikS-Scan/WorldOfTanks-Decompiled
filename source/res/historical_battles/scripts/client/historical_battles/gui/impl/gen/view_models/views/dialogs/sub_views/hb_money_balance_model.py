# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/dialogs/sub_views/hb_money_balance_model.py
from frameworks.wulf import Array
from historical_battles.gui.impl.gen.view_models.views.dialogs.sub_views.hb_money_balance_coin_model import HbMoneyBalanceCoinModel
from gui.impl.gen.view_models.views.dialogs.sub_views.money_balance_view_model import MoneyBalanceViewModel

class HbMoneyBalanceModel(MoneyBalanceViewModel):
    __slots__ = ()

    def __init__(self, properties=16, commands=0):
        super(HbMoneyBalanceModel, self).__init__(properties=properties, commands=commands)

    def getCoins(self):
        return self._getArray(11)

    def setCoins(self, value):
        self._setArray(11, value)

    @staticmethod
    def getCoinsType():
        return HbMoneyBalanceCoinModel

    def getIsCreditsVisible(self):
        return self._getBool(12)

    def setIsCreditsVisible(self, value):
        self._setBool(12, value)

    def getIsGoldVisible(self):
        return self._getBool(13)

    def setIsGoldVisible(self, value):
        self._setBool(13, value)

    def getIsCrystalsVisible(self):
        return self._getBool(14)

    def setIsCrystalsVisible(self, value):
        self._setBool(14, value)

    def getIsFreeExpVisible(self):
        return self._getBool(15)

    def setIsFreeExpVisible(self, value):
        self._setBool(15, value)

    def _initialize(self):
        super(HbMoneyBalanceModel, self)._initialize()
        self._addArrayProperty('coins', Array())
        self._addBoolProperty('isCreditsVisible', False)
        self._addBoolProperty('isGoldVisible', False)
        self._addBoolProperty('isCrystalsVisible', False)
        self._addBoolProperty('isFreeExpVisible', False)
