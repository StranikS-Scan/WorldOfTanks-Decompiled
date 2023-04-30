# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/exchange_with_items.py
import logging
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.buy_and_exchange_bottom_content_type import BuyAndExchangeBottomContentType
from gui.impl.gen.view_models.views.lobby.exchange.exchange_with_items_model import ExchangeWithItemsModel
from gui.impl.lobby.dialogs.auxiliary.buy_and_exchange_state_machine import BuyAndExchangeStateEnum
from gui.impl.lobby.dialogs.buy_and_exchange import BuyAndExchange
from gui.impl.lobby.dialogs.contents.exchange_content import ExchangeContentResult
from gui.impl.lobby.dialogs.contents.multiple_items_content import MultipleItemsContent
from gui.impl.lobby.dialogs.contents.multiple_items_content_to_upgrade import MultipleItemsContentToUpgrade
from gui.shared.money import ZERO_MONEY
from gui.shared.utils.requesters import REQ_CRITERIA
_logger = logging.getLogger(__name__)

class ExchangeWithItems(BuyAndExchange):
    __slots__ = ('__items', '__totalPrice', '_mainContent')

    def __init__(self, settings, items, price):
        self.__items = items
        self.__totalPrice = price
        self._mainContent = None
        super(ExchangeWithItems, self).__init__(settings=settings, price=self.__totalPrice, startState=BuyAndExchangeStateEnum.EXCHANGE_CONTENT)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ExchangeWithItems, self)._onLoading(*args, **kwargs)
        contentClass = self._getContentClass()
        self._mainContent = contentClass(viewModel=self.viewModel.mainContent, items=self.__items)
        self._mainContent.onLoading()

    def _initialize(self, *args, **kwargs):
        super(ExchangeWithItems, self)._initialize()
        if self._mainContent is not None:
            self._mainContent.initialize()
        return

    def _finalize(self):
        if self._mainContent is not None:
            self._mainContent.finalize()
        super(ExchangeWithItems, self)._finalize()
        return

    def _exchangeComplete(self, result):
        if result == ExchangeContentResult.IS_OK:
            self._onAccept()

    def _stateToContent(self):
        return {BuyAndExchangeStateEnum.EXCHANGE_CONTENT: BuyAndExchangeBottomContentType.EXCHANGE_PANEL,
         BuyAndExchangeStateEnum.EXCHANGE_IN_PROCESS: BuyAndExchangeBottomContentType.EXCHANGE_PANEL,
         BuyAndExchangeStateEnum.GOLD_NOT_ENOUGH: BuyAndExchangeBottomContentType.EXCHANGE_PANEL,
         BuyAndExchangeStateEnum.EXCHANGE_NOT_REQUIRED: BuyAndExchangeBottomContentType.EXCHANGE_PANEL}

    @classmethod
    def _getContentClass(cls):
        return MultipleItemsContent


class ExchangeToBuyItems(ExchangeWithItems):
    __slots__ = ()

    def __init__(self, itemsCountMap):
        settings = ViewSettings(layoutID=R.views.lobby.tanksetup.dialogs.ExchangeToBuyItems(), model=ExchangeWithItemsModel())
        itemsCountMap = itemsCountMap
        items = self._itemsCache.items.getItems(criteria=REQ_CRITERIA.CUSTOM(lambda i: i.intCD in itemsCountMap)).values()
        super(ExchangeToBuyItems, self).__init__(settings=settings, items=items, price=sum([ item.getBuyPrice().price * itemsCountMap[item.intCD] for item in items ], ZERO_MONEY))


class ExchangeToUpgradeDevice(ExchangeWithItems):
    __slots__ = ()

    def __init__(self, device):
        if not device.isUpgradable:
            _logger.warning("Device doesn't upgradable!")
        settings = ViewSettings(layoutID=R.views.lobby.tanksetup.dialogs.ExchangeToUpgradeItems(), model=ExchangeWithItemsModel())
        super(ExchangeToUpgradeDevice, self).__init__(settings=settings, items=[device], price=device.getUpgradePrice(self._itemsCache.items).price if device.isUpgradable else ZERO_MONEY)

    @classmethod
    def _getContentClass(cls):
        return MultipleItemsContentToUpgrade
