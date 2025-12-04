# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/pet/pet_shop/shop_card.py
from frameworks.wulf import Array
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_indicator_type import NyIndicatorType
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.pet_shop.price_range import PriceRange

class ShopCard(NyIndicatorType):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(ShopCard, self).__init__(properties=properties, commands=commands)

    def getIsProgressionPrices(self):
        return self._getBool(1)

    def setIsProgressionPrices(self, value):
        self._setBool(1, value)

    def getLoyaltyPoints(self):
        return self._getNumber(2)

    def setLoyaltyPoints(self, value):
        self._setNumber(2, value)

    def getVitalityPoints(self):
        return self._getNumber(3)

    def setVitalityPoints(self, value):
        self._setNumber(3, value)

    def getItemsInInventory(self):
        return self._getNumber(4)

    def setItemsInInventory(self, value):
        self._setNumber(4, value)

    def getIsWaiting(self):
        return self._getBool(5)

    def setIsWaiting(self, value):
        self._setBool(5, value)

    def getIsLocked(self):
        return self._getBool(6)

    def setIsLocked(self, value):
        self._setBool(6, value)

    def getLettersToUnlock(self):
        return self._getNumber(7)

    def setLettersToUnlock(self, value):
        self._setNumber(7, value)

    def getPriceRanges(self):
        return self._getArray(8)

    def setPriceRanges(self, value):
        self._setArray(8, value)

    @staticmethod
    def getPriceRangesType():
        return PriceRange

    def getCount(self):
        return self._getNumber(9)

    def setCount(self, value):
        self._setNumber(9, value)

    def getId(self):
        return self._getNumber(10)

    def setId(self, value):
        self._setNumber(10, value)

    def getCurrentPointPrice(self):
        return self._getNumber(11)

    def setCurrentPointPrice(self, value):
        self._setNumber(11, value)

    def getCurrentPrice(self):
        return self._getNumber(12)

    def setCurrentPrice(self, value):
        self._setNumber(12, value)

    def _initialize(self):
        super(ShopCard, self)._initialize()
        self._addBoolProperty('isProgressionPrices', True)
        self._addNumberProperty('loyaltyPoints', 0)
        self._addNumberProperty('vitalityPoints', 0)
        self._addNumberProperty('itemsInInventory', 0)
        self._addBoolProperty('isWaiting', False)
        self._addBoolProperty('isLocked', False)
        self._addNumberProperty('lettersToUnlock', 0)
        self._addArrayProperty('priceRanges', Array())
        self._addNumberProperty('count', 0)
        self._addNumberProperty('id', 0)
        self._addNumberProperty('currentPointPrice', 0)
        self._addNumberProperty('currentPrice', 0)
