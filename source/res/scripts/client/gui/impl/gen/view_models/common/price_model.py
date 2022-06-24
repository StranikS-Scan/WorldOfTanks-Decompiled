# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/price_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel

class PriceModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PriceModel, self).__init__(properties=properties, commands=commands)

    def getPrice(self):
        return self._getArray(0)

    def setPrice(self, value):
        self._setArray(0, value)

    @staticmethod
    def getPriceType():
        return PriceItemModel

    def getDefPrice(self):
        return self._getArray(1)

    def setDefPrice(self, value):
        self._setArray(1, value)

    @staticmethod
    def getDefPriceType():
        return PriceItemModel

    def getDiscount(self):
        return self._getArray(2)

    def setDiscount(self, value):
        self._setArray(2, value)

    @staticmethod
    def getDiscountType():
        return PriceItemModel

    def _initialize(self):
        super(PriceModel, self)._initialize()
        self._addArrayProperty('price', Array())
        self._addArrayProperty('defPrice', Array())
        self._addArrayProperty('discount', Array())
