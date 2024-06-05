# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/base_product_model.py
from enum import Enum, IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.product_price_model import ProductPriceModel

class Rank(IntEnum):
    FIRST = 6
    SECOND = 5
    THIRD = 4
    FOURTH = 3
    FIFTH = 2
    SIXTH = 1


class ProductTypes(IntEnum):
    BASE = 0
    VEHICLE = 1
    STYLE3D = 2
    REWARD = 3


class ProductState(Enum):
    LOCKED = 'locked'
    READYTORESTORE = 'readyToRestore'
    READYTOPURCHASE = 'readyToPurchase'
    PURCHASED = 'purchased'
    INPROGRESS = 'inProgress'


class BaseProductModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(BaseProductModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return ProductPriceModel

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def getType(self):
        return ProductTypes(self._getNumber(2))

    def setType(self, value):
        self._setNumber(2, value.value)

    def getRank(self):
        return Rank(self._getNumber(3))

    def setRank(self, value):
        self._setNumber(3, value.value)

    def getLimitedQuantity(self):
        return self._getNumber(4)

    def setLimitedQuantity(self, value):
        self._setNumber(4, value)

    def getState(self):
        return ProductState(self._getString(5))

    def setState(self, value):
        self._setString(5, value.value)

    def getIsNew(self):
        return self._getBool(6)

    def setIsNew(self, value):
        self._setBool(6, value)

    def getDescription(self):
        return self._getString(7)

    def setDescription(self, value):
        self._setString(7, value)

    def getTooltipId(self):
        return self._getString(8)

    def setTooltipId(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(BaseProductModel, self)._initialize()
        self._addViewModelProperty('price', ProductPriceModel())
        self._addNumberProperty('id', 0)
        self._addNumberProperty('type')
        self._addNumberProperty('rank')
        self._addNumberProperty('limitedQuantity', 0)
        self._addStringProperty('state')
        self._addBoolProperty('isNew', False)
        self._addStringProperty('description', '')
        self._addStringProperty('tooltipId', '')
