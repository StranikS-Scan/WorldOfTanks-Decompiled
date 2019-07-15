# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/cart_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_compound_price_model import UserCompoundPriceModel
from gui.impl.wrappers.user_list_model import UserListModel

class CartModel(ViewModel):
    __slots__ = ('onSelectItem', 'onSelectAutoRent', 'onBuyAction', 'onTutorialClose')

    @property
    def seasons(self):
        return self._getViewModel(0)

    @property
    def totalPrice(self):
        return self._getViewModel(1)

    def getIsStyle(self):
        return self._getBool(2)

    def setIsStyle(self, value):
        self._setBool(2, value)

    def getStyleTypeName(self):
        return self._getString(3)

    def setStyleTypeName(self, value):
        self._setString(3, value)

    def getStyleName(self):
        return self._getString(4)

    def setStyleName(self, value):
        self._setString(4, value)

    def getHasAutoRent(self):
        return self._getBool(5)

    def setHasAutoRent(self, value):
        self._setBool(5, value)

    def getIsAutoRentSelected(self):
        return self._getBool(6)

    def setIsAutoRentSelected(self, value):
        self._setBool(6, value)

    def getIsShopEnabled(self):
        return self._getBool(7)

    def setIsShopEnabled(self, value):
        self._setBool(7, value)

    def getIsAnySelected(self):
        return self._getBool(8)

    def setIsAnySelected(self, value):
        self._setBool(8, value)

    def getIsEnoughMoney(self):
        return self._getBool(9)

    def setIsEnoughMoney(self, value):
        self._setBool(9, value)

    def getIsRentable(self):
        return self._getBool(10)

    def setIsRentable(self, value):
        self._setBool(10, value)

    def getRentCount(self):
        return self._getNumber(11)

    def setRentCount(self, value):
        self._setNumber(11, value)

    def getPurchasedCount(self):
        return self._getNumber(12)

    def setPurchasedCount(self, value):
        self._setNumber(12, value)

    def getIsProlongStyleRent(self):
        return self._getBool(13)

    def setIsProlongStyleRent(self, value):
        self._setBool(13, value)

    def getShowProlongHint(self):
        return self._getBool(14)

    def setShowProlongHint(self, value):
        self._setBool(14, value)

    def _initialize(self):
        super(CartModel, self)._initialize()
        self._addViewModelProperty('seasons', UserListModel())
        self._addViewModelProperty('totalPrice', UserCompoundPriceModel())
        self._addBoolProperty('isStyle', False)
        self._addStringProperty('styleTypeName', '')
        self._addStringProperty('styleName', '')
        self._addBoolProperty('hasAutoRent', False)
        self._addBoolProperty('isAutoRentSelected', False)
        self._addBoolProperty('isShopEnabled', False)
        self._addBoolProperty('isAnySelected', False)
        self._addBoolProperty('isEnoughMoney', False)
        self._addBoolProperty('isRentable', False)
        self._addNumberProperty('rentCount', 0)
        self._addNumberProperty('purchasedCount', 0)
        self._addBoolProperty('isProlongStyleRent', False)
        self._addBoolProperty('showProlongHint', False)
        self.onSelectItem = self._addCommand('onSelectItem')
        self.onSelectAutoRent = self._addCommand('onSelectAutoRent')
        self.onBuyAction = self._addCommand('onBuyAction')
        self.onTutorialClose = self._addCommand('onTutorialClose')
