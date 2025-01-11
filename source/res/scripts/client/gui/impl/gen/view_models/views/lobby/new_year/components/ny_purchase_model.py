# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_purchase_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.balance_model import BalanceModel

class PurchaseState(Enum):
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'
    LOCKED = 'locked'


class NyPurchaseModel(ViewModel):
    __slots__ = ('onBuy', 'onBuyGold')

    def __init__(self, properties=5, commands=2):
        super(NyPurchaseModel, self).__init__(properties=properties, commands=commands)

    def getBalance(self):
        return self._getArray(0)

    def setBalance(self, value):
        self._setArray(0, value)

    @staticmethod
    def getBalanceType():
        return BalanceModel

    def getCurrency(self):
        return self._getString(1)

    def setCurrency(self, value):
        self._setString(1, value)

    def getPrice(self):
        return self._getNumber(2)

    def setPrice(self, value):
        self._setNumber(2, value)

    def getIsEnough(self):
        return self._getBool(3)

    def setIsEnough(self, value):
        self._setBool(3, value)

    def getPurchaseState(self):
        return PurchaseState(self._getString(4))

    def setPurchaseState(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(NyPurchaseModel, self)._initialize()
        self._addArrayProperty('balance', Array())
        self._addStringProperty('currency', '')
        self._addNumberProperty('price', 0)
        self._addBoolProperty('isEnough', False)
        self._addStringProperty('purchaseState')
        self.onBuy = self._addCommand('onBuy')
        self.onBuyGold = self._addCommand('onBuyGold')
