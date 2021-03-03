# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bm2021/dialogs/black_market_exchange_currency.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.bm2021.dialogs.black_market_exchange_currency_model import BlackMarketExchangeCurrencyModel
from gui.impl.lobby.bm2021.sound import BLACK_MARKET_OVERLAY_SOUND_SPACE
from gui.impl.lobby.dialogs.buy_and_exchange import BuyAndExchange
from gui.impl.lobby.dialogs.contents.exchange_content import ExchangeContentResult
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_ZERO
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class BlackMarketExchangeCurrency(BuyAndExchange):
    __slots__ = ('__price', '__titleResId', '__productName', '__productsAmount')
    _COMMON_SOUND_SPACE = BLACK_MARKET_OVERLAY_SOUND_SPACE
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.bm2021.dialogs.BlackMarketExchangeCurrency())
        settings.model = BlackMarketExchangeCurrencyModel()
        self.__price = kwargs.pop('price', ITEM_PRICE_ZERO)
        self.__titleResId = kwargs.pop('titleResId', R.strings.bm2021.dialog.exchangeGold.title())
        startState = kwargs.pop('startState', None)
        self.__productName = kwargs.pop('productName', '')
        self.__productsAmount = kwargs.pop('productsAmount', 0)
        super(BlackMarketExchangeCurrency, self).__init__(settings, price=self.__price.price, startState=startState)
        return

    @property
    def viewModel(self):
        return super(BlackMarketExchangeCurrency, self).getViewModel()

    def _setBaseParams(self, model):
        super(BlackMarketExchangeCurrency, self)._setBaseParams(model)
        model.setTitleBody(self.__titleResId)
        model.setProductName(self.__productName)
        model.setProductsAmount(self.__productsAmount)

    def _exchangeComplete(self, result):
        if result == ExchangeContentResult.IS_OK:
            self._onAccept()
