# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/shop_views/bundle_view_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.order_model import OrderModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.bundle_bonus_view_model import BundleBonusViewModel

class BundleLayout(Enum):
    NEWBIE = 'newbie'
    SPECIALIST = 'specialist'
    MEISTER = 'meister'


class BundleViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(BundleViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def order(self):
        return self._getViewModel(0)

    @staticmethod
    def getOrderType():
        return OrderModel

    def getId(self):
        return self._getString(1)

    def setId(self, value):
        self._setString(1, value)

    def getLayout(self):
        return BundleLayout(self._getString(2))

    def setLayout(self, value):
        self._setString(2, value.value)

    def getTitle(self):
        return self._getResource(3)

    def setTitle(self, value):
        self._setResource(3, value)

    def getDiscount(self):
        return self._getNumber(4)

    def setDiscount(self, value):
        self._setNumber(4, value)

    def getPrice(self):
        return self._getNumber(5)

    def setPrice(self, value):
        self._setNumber(5, value)

    def getCurrencyType(self):
        return self._getString(6)

    def setCurrencyType(self, value):
        self._setString(6, value)

    def getBuyCount(self):
        return self._getNumber(7)

    def setBuyCount(self, value):
        self._setNumber(7, value)

    def getBonuses(self):
        return self._getArray(8)

    def setBonuses(self, value):
        self._setArray(8, value)

    @staticmethod
    def getBonusesType():
        return BundleBonusViewModel

    def _initialize(self):
        super(BundleViewModel, self)._initialize()
        self._addViewModelProperty('order', OrderModel())
        self._addStringProperty('id', '')
        self._addStringProperty('layout')
        self._addResourceProperty('title', R.invalid())
        self._addNumberProperty('discount', 0)
        self._addNumberProperty('price', 0)
        self._addStringProperty('currencyType', '')
        self._addNumberProperty('buyCount', 0)
        self._addArrayProperty('bonuses', Array())
