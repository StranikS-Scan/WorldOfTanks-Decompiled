# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/buy_and_exchange.py
import logging
import typing
from gui.impl.gen.view_models.views.lobby.common.exchange_dialog_state import ExchangeDialogState
from gui.impl.lobby.dialogs.contents.exchange_content import ExchangeContentResult
from gui.impl.lobby.tank_setup.dialogs.bottom_content.bottom_contents import ExchangePriceBottomContent
from gui.shared.utils import decorators
from gui.impl.gen.view_models.views.lobby.common.dialog_with_exchange import DialogWithExchange
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.impl.lobby.dialogs.auxiliary.buy_and_exchange_state_machine import BuyAndExchangeStateEnum, BuyAndExchangeStateMachine, BuyAndExchangeEventEnum
from gui.shared.gui_items.fitting_item import canBuyWithGoldExchange
from gui.shared.money import Currency
from gui.impl.gen.view_models.views.lobby.common.buy_and_exchange_bottom_content_type import BuyAndExchangeBottomContentType
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewSettings
    from gui.shared.money import Money
TViewModel = typing.TypeVar('TViewModel', bound=DialogWithExchange)
_logger = logging.getLogger(__name__)

class BuyAndExchange(FullScreenDialogView, typing.Generic[TViewModel]):
    __slots__ = ('_exchangeContent', '__stateMachine', '__price')

    def __init__(self, settings, price, startState=None):
        super(BuyAndExchange, self).__init__(settings)
        self._exchangeContent = None
        self.__price = price
        self.__stateMachine = BuyAndExchangeStateMachine(handler=self, stateToContent=self._stateToContent(), startState=startState if startState else self._getStartStateByStats())
        return

    def stateChanged(self, stateID):
        currentContentType = self.__stateMachine.getCurrentContentType()
        if stateID == BuyAndExchangeStateEnum.EXCHANGE_IN_PROCESS:
            if self._exchangeContent is not None:
                self.__exchange()
        elif stateID == BuyAndExchangeStateEnum.EXCHANGE_CONTENT:
            self._transitToExchange()
            self.viewModel.setBottomContentType(currentContentType)
        else:
            self.viewModel.setBottomContentType(currentContentType)
        if currentContentType == BuyAndExchangeBottomContentType.EXCHANGE_PANEL:
            self.viewModel.setExchangeState(self.__getExchangePanelState(stateID))
        elif self.viewModel.getExchangeState() != ExchangeDialogState.DEFAULT:
            self.viewModel.setExchangeState(ExchangeDialogState.DEFAULT)
        return

    def _onLoading(self, *args, **kwargs):
        super(BuyAndExchange, self)._onLoading(*args, **kwargs)
        self._exchangeContent = self._createExchangeContent()
        self._exchangeContent.onLoading()
        self.viewModel.setBottomContentType(self.__stateMachine.getCurrentContentType())
        self.__setLacksMoney(self._stats.money.getShortage(self.__price), Currency.CREDITS)

    def _initialize(self, *args, **kwargs):
        super(BuyAndExchange, self)._initialize()
        if self._exchangeContent is not None:
            self._exchangeContent.initialize()
        self.__stateMachine.run()
        return

    def _finalize(self):
        self.__stateMachine.stop()
        if self._exchangeContent is not None:
            self._exchangeContent.finalize()
        super(BuyAndExchange, self)._finalize()
        return

    def _onInventoryResync(self, *args, **kwargs):
        super(BuyAndExchange, self)._onInventoryResync(*args, **kwargs)
        needItems = self._needItemsForExchange()
        if self._exchangeContent is not None and self.__stateMachine.getCurrentContentType() == BuyAndExchangeBottomContentType.EXCHANGE_PANEL:
            self._exchangeContent.update(needItems)
        needExchange = self._needExchange()
        self.__stateMachine.transit(BuyAndExchangeEventEnum.NEED_EXCHANGE, condition=lambda : needExchange)
        self.__stateMachine.transit(BuyAndExchangeEventEnum.CAN_BUY, condition=lambda : needItems == 0)
        self.__stateMachine.transit(BuyAndExchangeEventEnum.CAN_NOT_BUY, condition=lambda : needItems > 0 and not needExchange)
        self.__setLacksMoney(self._stats.money.getShortage(self.__price), Currency.CREDITS)
        return

    def _onAcceptClicked(self):
        if self.__stateMachine.isCurrentState(BuyAndExchangeStateEnum.BUY_CONTENT):
            self._buyAccept()
        elif self.__stateMachine.isCurrentState(BuyAndExchangeStateEnum.BUY_NOT_REQUIRED):
            self._buyNotRequiredAccept()
        elif self.__acceptShouldDisabled():
            _logger.warning('Accept button should be disabled')
        else:
            self.__stateMachine.transit(BuyAndExchangeEventEnum.ACCEPT_CLICKED)

    def _stateToContent(self):
        return {BuyAndExchangeStateEnum.BUY_CONTENT: BuyAndExchangeBottomContentType.DEAL_PANEL,
         BuyAndExchangeStateEnum.NEED_EXCHANGE: BuyAndExchangeBottomContentType.DEAL_PANEL,
         BuyAndExchangeStateEnum.CAN_NOT_BUY: BuyAndExchangeBottomContentType.DEAL_PANEL,
         BuyAndExchangeStateEnum.EXCHANGE_CONTENT: BuyAndExchangeBottomContentType.EXCHANGE_PANEL,
         BuyAndExchangeStateEnum.EXCHANGE_IN_PROCESS: BuyAndExchangeBottomContentType.EXCHANGE_PANEL,
         BuyAndExchangeStateEnum.GOLD_NOT_ENOUGH: BuyAndExchangeBottomContentType.EXCHANGE_PANEL,
         BuyAndExchangeStateEnum.EXCHANGE_NOT_REQUIRED: BuyAndExchangeBottomContentType.EXCHANGE_PANEL}

    def _getStartStateByStats(self):
        if self._needExchange():
            return BuyAndExchangeStateEnum.EXCHANGE_CONTENT
        return BuyAndExchangeStateEnum.CAN_NOT_BUY if self._needItemsForExchange() > 0 else BuyAndExchangeStateEnum.BUY_CONTENT

    def _needExchange(self):
        canBuy = canBuyWithGoldExchange(self.__price, self._stats.money, self._itemsCache.items.shop.exchangeRate)
        return canBuy and self._needItemsForExchange() > 0

    def _transitToExchange(self):
        if self._exchangeContent is not None:
            self._exchangeContent.update(self._needItemsForExchange())
        self.__setLacksMoney(self._stats.money.getShortage(self.__price), Currency.CREDITS)
        return

    def _exchangeComplete(self, result):
        pass

    def _createExchangeContent(self):
        return ExchangePriceBottomContent(fromCurrency=Currency.GOLD, toCurrency=Currency.CREDITS, viewModel=self.viewModel.exchangePanel, needItem=self._needItemsForExchange())

    def _needItemsForExchange(self):
        return self._stats.money.getShortage(self.__price).get(Currency.CREDITS, default=0)

    def _buyAccept(self):
        self._onAccept()

    def _buyNotRequiredAccept(self):
        self._onCancel()

    def _updatePrice(self, price):
        self.__price = price

    def _getCurrentDialogState(self):
        return self.__stateMachine.getCurrentState()

    @decorators.process('transferMoney')
    def __exchange(self):
        result = yield self._exchangeContent.exchange()
        self._exchangeComplete(result)
        if result == ExchangeContentResult.SERVER_ERROR:
            self._onCancel()
        elif result == ExchangeContentResult.IS_OK:
            self.__stateMachine.transit(BuyAndExchangeEventEnum.EXCHANGE_COMPLETED)
        elif result == ExchangeContentResult.INVALID_VALUE:
            self.__stateMachine.transit(BuyAndExchangeEventEnum.EXCHANGE_VALIDATION_ERROR)

    def __getExchangePanelState(self, stateID):
        if stateID in (BuyAndExchangeStateEnum.GOLD_NOT_ENOUGH, BuyAndExchangeStateEnum.CAN_NOT_BUY):
            return ExchangeDialogState.NOT_POSSIBLE
        return ExchangeDialogState.NOT_REQUIRED if stateID == BuyAndExchangeStateEnum.EXCHANGE_NOT_REQUIRED else ExchangeDialogState.DEFAULT

    def __acceptShouldDisabled(self):
        return self.__stateMachine.getCurrentState() in (BuyAndExchangeStateEnum.CAN_NOT_BUY, BuyAndExchangeStateEnum.GOLD_NOT_ENOUGH, BuyAndExchangeStateEnum.EXCHANGE_NOT_REQUIRED)

    def __setLacksMoney(self, lacksMoney, currencyType):
        with self.viewModel.transaction() as model:
            model.lacksMoney.setValue(lacksMoney.get(currencyType, default=0))
            model.lacksMoney.setName(currencyType)
