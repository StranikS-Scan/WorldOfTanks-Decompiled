# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/shop_views/optional_device_item_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.bonuses_model import BonusesModel
from historical_battles.gui.impl.gen.view_models.views.common.multi_price_view_model import MultiPriceViewModel

class OptionalDeviceItemViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(OptionalDeviceItemViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return MultiPriceViewModel

    @property
    def bonuses(self):
        return self._getViewModel(1)

    @staticmethod
    def getBonusesType():
        return BonusesModel

    def getId(self):
        return self._getString(2)

    def setId(self, value):
        self._setString(2, value)

    def getIcon(self):
        return self._getString(3)

    def setIcon(self, value):
        self._setString(3, value)

    def getBuyCount(self):
        return self._getNumber(4)

    def setBuyCount(self, value):
        self._setNumber(4, value)

    def getOverlayType(self):
        return self._getString(5)

    def setOverlayType(self, value):
        self._setString(5, value)

    def getEffect(self):
        return self._getResource(6)

    def setEffect(self, value):
        self._setResource(6, value)

    def _initialize(self):
        super(OptionalDeviceItemViewModel, self)._initialize()
        self._addViewModelProperty('price', MultiPriceViewModel())
        self._addViewModelProperty('bonuses', BonusesModel())
        self._addStringProperty('id', '')
        self._addStringProperty('icon', '')
        self._addNumberProperty('buyCount', 0)
        self._addStringProperty('overlayType', '')
        self._addResourceProperty('effect', R.invalid())
