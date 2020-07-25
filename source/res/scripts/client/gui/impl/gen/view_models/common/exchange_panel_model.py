# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/exchange_panel_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.exchange_rate_model import ExchangeRateModel
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel

class ExchangePanelModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ExchangePanelModel, self).__init__(properties=properties, commands=commands)

    @property
    def fromItem(self):
        return self._getViewModel(0)

    @property
    def toItem(self):
        return self._getViewModel(1)

    @property
    def exchangeRate(self):
        return self._getViewModel(2)

    def _initialize(self):
        super(ExchangePanelModel, self)._initialize()
        self._addViewModelProperty('fromItem', PriceItemModel())
        self._addViewModelProperty('toItem', PriceItemModel())
        self._addViewModelProperty('exchangeRate', ExchangeRateModel())
