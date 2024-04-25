# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/shop_views/bundle_item_view_model.py
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.common.multi_price_view_model import MultiPriceViewModel

class BundleItemViewModel(ViewModel):
    __slots__ = ()
    VEHICLE = 'vehicle'
    EQUIPMENTS = 'equipments'

    def __init__(self, properties=5, commands=0):
        super(BundleItemViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return MultiPriceViewModel

    def getIsBought(self):
        return self._getBool(1)

    def setIsBought(self, value):
        self._setBool(1, value)

    def getBuyCount(self):
        return self._getNumber(2)

    def setBuyCount(self, value):
        self._setNumber(2, value)

    def getDiscountValue(self):
        return self._getNumber(3)

    def setDiscountValue(self, value):
        self._setNumber(3, value)

    def getType(self):
        return self._getString(4)

    def setType(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(BundleItemViewModel, self)._initialize()
        self._addViewModelProperty('price', MultiPriceViewModel())
        self._addBoolProperty('isBought', False)
        self._addNumberProperty('buyCount', 0)
        self._addNumberProperty('discountValue', 0)
        self._addStringProperty('type', '')
