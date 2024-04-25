# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/shared/gui_items/processors/hb_coin.py
from gui.impl.backport import text, getIntegralFormat
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items.processors import Processor, plugins, makeSuccess
from gui.shared.gui_items.processors.plugins import SyncValidator
from gui.shared.money import Money
from helpers import dependency
from historical_battles.gui.system_messages import HB_SM_TYPE
from historical_battles.skeletons.gui.game_event_controller import IGameEventController

class HBCoinsExchangeValidator(SyncValidator):
    __slots__ = ('_coinsToGive', '_coinsToGet', '_count')
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, coinsToGive, coinsToGet, count):
        super(HBCoinsExchangeValidator, self).__init__()
        self._coinsToGive = coinsToGive
        self._coinsToGet = coinsToGet
        self._count = count

    def _validate(self):
        return plugins.makeError(text(R.strings.hb_shop.errors.serverError())) if self._areEqual() or self._notEnoughCoins() or self._notEnoughCredits() or self._exchangeDisabled() or self._isAnyEmpty() else plugins.makeSuccess()

    def _areEqual(self):
        return self._coinsToGet == self._coinsToGive

    def _isAnyEmpty(self):
        return not self._coinsToGet or not self._coinsToGive

    def _notEnoughCredits(self):
        currency, amount = self._gameEventController.coins.getExchangePrice(self._coinsToGive)
        exchangePrice = Money.makeFrom(currency, amount) * self._count
        shortage = self.itemsCache.items.stats.money.getShortage(exchangePrice)
        return bool(shortage)

    def _notEnoughCoins(self):
        haveCoins = self._gameEventController.coins.getCount(self._coinsToGive)
        return haveCoins < self._count

    def _exchangeDisabled(self):
        return not self._gameEventController.coins.isExchangeEnabled(self._coinsToGive) or not self._gameEventController.coins.isExchangeEnabled(self._coinsToGet) or not self._gameEventController.coins.isExchangeStarted(self._coinsToGive) or not self._gameEventController.coins.isExchangeStarted(self._coinsToGet)


class HBCoinsExchangeProcessor(Processor):
    __slots__ = ('_coinsToGive', '_coinsToGet', '_count')
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, coinsToGive, coinsToGet, count):
        pluginList = (HBCoinsExchangeValidator(coinsToGive, coinsToGet, count),)
        super(HBCoinsExchangeProcessor, self).__init__(plugins=pluginList)
        self._coinsToGive = coinsToGive
        self._coinsToGet = coinsToGet
        self._count = count

    def _request(self, callback):
        self._gameEventController.coins.exchange(self._coinsToGive, self._coinsToGet, self._count, lambda requestID, code, errorCode, *args, **kwargs: self._response(code, callback, errorCode))

    def _successHandler(self, code, ctx=None):
        currency, amount = self._gameEventController.coins.getExchangePrice(self._coinsToGive)
        exchangePrice = Money.makeFrom(currency, amount) * self._count
        creditAmount = getIntegralFormat(exchangePrice.credits)
        userMsg = text_styles.concatStylesToMultiLine(text(R.strings.hb_shop.coins_exchange.systemMessage.exchangeComplete()), text(R.strings.hb_coin.coins_exchange.systemMessage.received.dyn(self._coinsToGet)(), amount=text_styles.stats(getIntegralFormat(int(self._count)))), text(R.strings.hb_coin.coins_exchange.systemMessage.spent.dyn(self._coinsToGive)(), amount=getIntegralFormat(int(self._count))), text(R.strings.hb_shop.coins_exchange.systemMessage.creditsSpent(), amount=creditAmount))
        return makeSuccess(userMsg=userMsg, msgType=HB_SM_TYPE.FinancialOperationCredits, auxData=ctx)
