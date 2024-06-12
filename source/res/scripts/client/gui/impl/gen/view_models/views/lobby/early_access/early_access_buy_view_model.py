# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/early_access/early_access_buy_view_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.early_access.early_access_vehicle_model import EarlyAccessVehicleModel

class BuyResult(IntEnum):
    NONE = 0
    SUCCESS = 1
    FAIL = 2


class EarlyAccessBuyViewModel(ViewModel):
    __slots__ = ('onAboutEvent', 'onBuyTokens', 'onBackToPrevScreen')
    ARG_BUY_TOKENS_AMOUNT = 'tokens'

    def __init__(self, properties=10, commands=3):
        super(EarlyAccessBuyViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def getBuyResult(self):
        return BuyResult(self._getNumber(1))

    def setBuyResult(self, value):
        self._setNumber(1, value.value)

    def getFromTimestamp(self):
        return self._getNumber(2)

    def setFromTimestamp(self, value):
        self._setNumber(2, value)

    def getToTimestamp(self):
        return self._getNumber(3)

    def setToTimestamp(self, value):
        self._setNumber(3, value)

    def getTotalTokensCount(self):
        return self._getNumber(4)

    def setTotalTokensCount(self, value):
        self._setNumber(4, value)

    def getRecievedTokensCount(self):
        return self._getNumber(5)

    def setRecievedTokensCount(self, value):
        self._setNumber(5, value)

    def getCurrentTokensBalance(self):
        return self._getNumber(6)

    def setCurrentTokensBalance(self, value):
        self._setNumber(6, value)

    def getTokenPriceInGold(self):
        return self._getNumber(7)

    def setTokenPriceInGold(self, value):
        self._setNumber(7, value)

    def getGoldBalance(self):
        return self._getNumber(8)

    def setGoldBalance(self, value):
        self._setNumber(8, value)

    def getVehicles(self):
        return self._getArray(9)

    def setVehicles(self, value):
        self._setArray(9, value)

    @staticmethod
    def getVehiclesType():
        return EarlyAccessVehicleModel

    def _initialize(self):
        super(EarlyAccessBuyViewModel, self)._initialize()
        self._addStringProperty('state', '')
        self._addNumberProperty('buyResult', BuyResult.NONE.value)
        self._addNumberProperty('fromTimestamp', 0)
        self._addNumberProperty('toTimestamp', 0)
        self._addNumberProperty('totalTokensCount', 0)
        self._addNumberProperty('recievedTokensCount', 0)
        self._addNumberProperty('currentTokensBalance', 0)
        self._addNumberProperty('tokenPriceInGold', 0)
        self._addNumberProperty('goldBalance', 0)
        self._addArrayProperty('vehicles', Array())
        self.onAboutEvent = self._addCommand('onAboutEvent')
        self.onBuyTokens = self._addCommand('onBuyTokens')
        self.onBackToPrevScreen = self._addCommand('onBackToPrevScreen')
