# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/bm2021/dialogs/black_market_exchange_currency_model.py
from gui.impl.gen.view_models.views.lobby.common.dialog_with_exchange import DialogWithExchange
from gui.impl.gen.view_models.views.lobby.common.multiple_items_content_model import MultipleItemsContentModel

class BlackMarketExchangeCurrencyModel(DialogWithExchange):
    __slots__ = ()

    def __init__(self, properties=17, commands=3):
        super(BlackMarketExchangeCurrencyModel, self).__init__(properties=properties, commands=commands)

    @property
    def mainContent(self):
        return self._getViewModel(14)

    def getProductName(self):
        return self._getString(15)

    def setProductName(self, value):
        self._setString(15, value)

    def getProductsAmount(self):
        return self._getNumber(16)

    def setProductsAmount(self, value):
        self._setNumber(16, value)

    def _initialize(self):
        super(BlackMarketExchangeCurrencyModel, self)._initialize()
        self._addViewModelProperty('mainContent', MultipleItemsContentModel())
        self._addStringProperty('productName', '')
        self._addNumberProperty('productsAmount', 0)
