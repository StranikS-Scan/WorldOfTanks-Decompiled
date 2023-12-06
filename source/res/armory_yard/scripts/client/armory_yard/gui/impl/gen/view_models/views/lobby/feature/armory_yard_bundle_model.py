# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_bundle_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_model import PriceModel

class BundleType(Enum):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'


class ArmoryYardBundleModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(ArmoryYardBundleModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return PriceModel

    def getIndex(self):
        return self._getString(1)

    def setIndex(self, value):
        self._setString(1, value)

    def getType(self):
        return BundleType(self._getString(2))

    def setType(self, value):
        self._setString(2, value.value)

    def getLevelCount(self):
        return self._getNumber(3)

    def setLevelCount(self, value):
        self._setNumber(3, value)

    def getDiscountPercent(self):
        return self._getNumber(4)

    def setDiscountPercent(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(ArmoryYardBundleModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addStringProperty('index', '')
        self._addStringProperty('type')
        self._addNumberProperty('levelCount', 0)
        self._addNumberProperty('discountPercent', 0)
