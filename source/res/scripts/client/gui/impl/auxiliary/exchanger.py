# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/exchanger.py
import logging
import typing
from adisp import adisp_async, adisp_process
from gui.shared.gui_items.processors.common import GoldToCreditsExchanger
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IExchangeRatesWithDiscountsProvider
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class ExchangeSubmitterBase(object):

    @adisp_async
    def submit(self, fromItemCount, toItemCount, callback=None):
        pass

    def getCurrentRate(self):
        pass

    def getDefaultRate(self):
        pass

    def calculateToItemCount(self, fromExchangeAmount):
        pass

    def calculateFromItemCount(self, toExchangeAmount):
        pass


class ExchangeCreditsSubmitter(ExchangeSubmitterBase):
    __itemsCache = dependency.descriptor(IItemsCache)
    __exchangeRatesProvider = dependency.descriptor(IExchangeRatesWithDiscountsProvider)

    @adisp_async
    @adisp_process
    def submit(self, goldToExchange, withConfirm=True, callback=None):
        result = yield GoldToCreditsExchanger(goldToExchange, withConfirm=withConfirm).request()
        if callback is not None:
            callback(result)
        return

    @property
    def exchangeRate(self):
        return self.__exchangeRatesProvider.goldToCredits

    def getCurrentRate(self):
        return self.exchangeRate.discountRate.resourceRateValue

    def getDefaultRate(self):
        return self.exchangeRate.unlimitedRateAfterMainDiscount.resourceRateValue

    def calculateToItemCount(self, fromExchangeAmount):
        return self.exchangeRate.calculateExchange(fromExchangeAmount)

    def calculateFromItemCount(self, toExchangeAmount):
        return self.exchangeRate.calculateResourceToExchange(toExchangeAmount)


_TYPE_TO_SUBMITTER_MAP = {(Currency.GOLD, Currency.CREDITS): ExchangeCreditsSubmitter()}

class Exchanger(object):
    __slots__ = ('__submitter', '__fromItemType', '__toItemType', 'onUpdated')

    def __init__(self, fromItemType, toItemType):
        submitter = _TYPE_TO_SUBMITTER_MAP.get((fromItemType, toItemType), None)
        if submitter is None:
            _logger.error('not supported exchange type: from %s to %s', fromItemType, toItemType)
            submitter = ExchangeSubmitterBase()
        self.__submitter = submitter
        self.__fromItemType = fromItemType
        self.__toItemType = toItemType
        return

    @adisp_async
    @adisp_process
    def tryExchange(self, fromItemCount, withConfirm=True, callback=None):
        result = yield self.__submitter.submit(fromItemCount, withConfirm=withConfirm)
        if callback is not None:
            callback(result)
        return

    def calculateToItemCount(self, fromItemCount):
        return self.__submitter.calculateToItemCount(fromItemCount)

    def calculateFromItemCount(self, toItemCount):
        return self.__submitter.calculateFromItemCount(toItemCount)

    def getCurrentRate(self):
        return self.__submitter.getCurrentRate()

    def getDefaultRate(self):
        return self.__submitter.getDefaultRate()
