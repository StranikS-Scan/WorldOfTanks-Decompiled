# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/cart_purchase_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_compound_price_model import UserCompoundPriceModel

class CartPurchaseModel(ViewModel):
    __slots__ = ('onBuyAction',)

    def __init__(self, properties=4, commands=1):
        super(CartPurchaseModel, self).__init__(properties=properties, commands=commands)

    @property
    def totalPrice(self):
        return self._getViewModel(0)

    def getPurchasedCount(self):
        return self._getNumber(1)

    def setPurchasedCount(self, value):
        self._setNumber(1, value)

    def getIsEnoughMoney(self):
        return self._getBool(2)

    def setIsEnoughMoney(self, value):
        self._setBool(2, value)

    def getIsShopEnabled(self):
        return self._getBool(3)

    def setIsShopEnabled(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(CartPurchaseModel, self)._initialize()
        self._addViewModelProperty('totalPrice', UserCompoundPriceModel())
        self._addNumberProperty('purchasedCount', 0)
        self._addBoolProperty('isEnoughMoney', False)
        self._addBoolProperty('isShopEnabled', False)
        self.onBuyAction = self._addCommand('onBuyAction')
