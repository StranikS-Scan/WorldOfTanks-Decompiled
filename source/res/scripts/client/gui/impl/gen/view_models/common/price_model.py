# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/price_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel

class PriceModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(PriceModel, self).__init__(properties=properties, commands=commands)

    def getPriceID(self):
        return self._getString(0)

    def setPriceID(self, value):
        self._setString(0, value)

    def getPrice(self):
        return self._getArray(1)

    def setPrice(self, value):
        self._setArray(1, value)

    @staticmethod
    def getPriceType():
        return PriceItemModel

    def getDefPrice(self):
        return self._getArray(2)

    def setDefPrice(self, value):
        self._setArray(2, value)

    @staticmethod
    def getDefPriceType():
        return PriceItemModel

    def getDiscount(self):
        return self._getArray(3)

    def setDiscount(self, value):
        self._setArray(3, value)

    @staticmethod
    def getDiscountType():
        return PriceItemModel

    def _initialize(self):
        super(PriceModel, self)._initialize()
        self._addStringProperty('priceID', '')
        self._addArrayProperty('price', Array())
        self._addArrayProperty('defPrice', Array())
        self._addArrayProperty('discount', Array())
