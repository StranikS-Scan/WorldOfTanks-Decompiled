# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/exchanger.py
import logging
import math
import typing
import Event
from adisp import async, process
from gui.shared.gui_items.processors.common import GoldToCreditsExchanger
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class ExchangeSubmitterBase(object):

    def __init__(self):
        self.onUpdated = Event.Event()

    def init(self):
        pass

    def fini(self):
        self.onUpdated.clear()

    @async
    def submit(self, fromItemCount, toItemCount, callback=None):
        pass

    def getCurrentRate(self):
        pass

    def getDefaultRate(self):
        pass


class ExchangeCreditsSubmitter(ExchangeSubmitterBase):
    __itemsCache = dependency.descriptor(IItemsCache)

    def init(self):
        super(ExchangeCreditsSubmitter, self).init()
        self.__itemsCache.onSyncCompleted += self.__update

    def fini(self):
        self.__itemsCache.onSyncCompleted -= self.__update
        self.onUpdated.clear()

    @async
    @process
    def submit(self, fromItemCount, toItemCount, withConfirm=True, callback=None):
        result = yield GoldToCreditsExchanger(fromItemCount, withConfirm=withConfirm).request()
        if callback is not None:
            callback(result)
        return

    def getCurrentRate(self):
        return self.__itemsCache.items.shop.exchangeRate

    def getDefaultRate(self):
        return self.__itemsCache.items.shop.defaults.exchangeRate

    def __update(self, *args, **kwargs):
        self.onUpdated()


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
        self.onUpdated = Event.Event()
        return

    def init(self):
        self.__submitter.init()
        self.__submitter.onUpdated += self.__updateRate

    def fini(self):
        self.__submitter.onUpdated -= self.__updateRate
        self.__submitter.fini()

    @async
    @process
    def tryExchange(self, fromItemCount, withConfirm=True, callback=None):
        result = yield self.__submitter.submit(fromItemCount, self.calculateToItemCount(fromItemCount), withConfirm=withConfirm)
        if callback is not None:
            callback(result)
        return

    def calculateToItemCount(self, fromItemCount):
        return fromItemCount * self.__submitter.getCurrentRate()

    def calculateFromItemCount(self, toItemCount):
        rate = self.__submitter.getCurrentRate()
        if rate:
            fromItemCount = int(math.ceil(float(toItemCount) / rate))
            return (fromItemCount, fromItemCount * rate)

    def getCurrentRate(self):
        return self.__submitter.getCurrentRate()

    def getDefaultRate(self):
        return self.__submitter.getDefaultRate()

    def getDiscount(self):
        defRate = float(self.getDefaultRate())
        rate = float(self.getCurrentRate())
        return int(math.floor((defRate - rate) / defRate * 100)) if rate and defRate and rate <= defRate else 0

    def __updateRate(self):
        self.onUpdated()
