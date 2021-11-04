# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/shop_sales.py
import BigWorld
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.shared.formatters import formatPrice
from gui.shared.gui_items.processors import Processor, makeI18nError, makeI18nSuccess
from gui.shared.money import Currency
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.game_control import IShopSalesEventController

class _ShopSalesEventProcessor(Processor):

    def __init__(self, silent=False):
        super(_ShopSalesEventProcessor, self).__init__()
        self.__silent = silent

    def _request(self, callback):
        self._getRequester()(lambda requestID, errorCode, resultData: self._response(errorCode, callback, ctx=resultData))

    def _getRequester(self):
        raise NotImplementedError

    def _makeSuccess(self, code, ctx=None):
        return makeI18nSuccess(auxData=ctx)

    def _makeError(self, code, ctx=None):
        return makeI18nError(auxData=ctx)

    def _successHandler(self, code, ctx=None):
        return self.__handleResponse(self._makeSuccess, code, ctx)

    def _errorHandler(self, code, _='', ctx=None):
        return self.__handleResponse(self._makeError, code, ctx)

    def __handleResponse(self, resultMaker, code, ctx):
        result = resultMaker(code, ctx)
        if not self.__silent:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        return result


class ShopSalesEventGetCurrentBundleProcessor(_ShopSalesEventProcessor):

    def __init__(self):
        super(ShopSalesEventGetCurrentBundleProcessor, self).__init__(True)

    def _getRequester(self):
        return BigWorld.player().shopSalesEvent.getCurrentBundle


class ShopSalesEventReRollProcessor(_ShopSalesEventProcessor):
    __shopSales = dependency.descriptor(IShopSalesEventController)
    __SYS_MESSAGE_TYPE = {Currency.GOLD: SM_TYPE.FinancialTransactionWithGold,
     Currency.CREDITS: SM_TYPE.FinancialTransactionWithCredits}

    def _getRequester(self):
        return BigWorld.player().shopSalesEvent.reRollBundle

    def _makeError(self, code, ctx=None):
        return makeI18nError(sysMsgKey='shop_sales_event/error', auxData=ctx)

    def _makeSuccess(self, code, ctx=None):
        price = self.__shopSales.reRollPrice
        transactionCurrency = findFirst(price.get, Currency.BY_WEIGHT, Currency.CREDITS)
        return makeI18nSuccess(sysMsgKey='shop_sales_event/success', money=formatPrice(price, ignoreZeros=True), type=self.__SYS_MESSAGE_TYPE.get(transactionCurrency, Currency.CREDITS), auxData=ctx)
