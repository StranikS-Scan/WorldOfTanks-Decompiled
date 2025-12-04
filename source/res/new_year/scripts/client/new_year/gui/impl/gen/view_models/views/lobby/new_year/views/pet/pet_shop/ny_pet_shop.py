# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/pet/pet_shop/ny_pet_shop.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.pet_shop.shop_card import ShopCard

class NyPetShop(ViewModel):
    __slots__ = ('onDialogClose', 'onDialogSubmit', 'onClose', 'onBuy', 'onAmountChange')

    def __init__(self, properties=7, commands=5):
        super(NyPetShop, self).__init__(properties=properties, commands=commands)

    def getIsShopEnabled(self):
        return self._getBool(0)

    def setIsShopEnabled(self, value):
        self._setBool(0, value)

    def getIsDialogScreen(self):
        return self._getBool(1)

    def setIsDialogScreen(self, value):
        self._setBool(1, value)

    def getIsEnough(self):
        return self._getBool(2)

    def setIsEnough(self, value):
        self._setBool(2, value)

    def getShopCards(self):
        return self._getArray(3)

    def setShopCards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getShopCardsType():
        return ShopCard

    def getLastPriceUpdateTime(self):
        return self._getNumber(4)

    def setLastPriceUpdateTime(self, value):
        self._setNumber(4, value)

    def getFullPrice(self):
        return self._getNumber(5)

    def setFullPrice(self, value):
        self._setNumber(5, value)

    def getIsBuyButtonEnabled(self):
        return self._getBool(6)

    def setIsBuyButtonEnabled(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(NyPetShop, self)._initialize()
        self._addBoolProperty('isShopEnabled', False)
        self._addBoolProperty('isDialogScreen', False)
        self._addBoolProperty('isEnough', True)
        self._addArrayProperty('shopCards', Array())
        self._addNumberProperty('lastPriceUpdateTime', 0)
        self._addNumberProperty('fullPrice', 0)
        self._addBoolProperty('isBuyButtonEnabled', False)
        self.onDialogClose = self._addCommand('onDialogClose')
        self.onDialogSubmit = self._addCommand('onDialogSubmit')
        self.onClose = self._addCommand('onClose')
        self.onBuy = self._addCommand('onBuy')
        self.onAmountChange = self._addCommand('onAmountChange')
