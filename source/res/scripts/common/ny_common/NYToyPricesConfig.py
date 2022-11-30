# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/NYToyPricesConfig.py
from typing import Dict, Union, Any, Callable
from ny_common.settings import NYToyPricesConsts

class NYToyPricesConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config):
        self._config = config

    def __contains__(self, item):
        return item in self._config

    def getToyPrice(self, toyID, default=None):
        return self._config.get(toyID, {}).get(NYToyPricesConsts.TOY_PRICE, default)

    def getDependencies(self, toyID):
        return self._config.get(toyID, {}).get(NYToyPricesConsts.TOY_DEPENDENCIES, {})

    def checkDependencies(self, toyID, tokensCountGetter):
        for dependencyName, dependencyData in self.getDependencies(toyID).iteritems():
            if dependencyName == NYToyPricesConsts.TOKENS_DEPENDENCIES:
                if any((tokensCountGetter(tokenID) < tokenCount for tokenID, tokenCount in dependencyData.iteritems())):
                    return False

        return True

    def getEndOfSale(self, toyID, eventEndTime, default=None):
        endOfSaleConfig = self._config.get(toyID, {}).get(NYToyPricesConsts.TOY_END_OF_SALE)
        if not endOfSaleConfig:
            return default
        for name, value in endOfSaleConfig.iteritems():
            if name == NYToyPricesConsts.END_OF_SALE_AT:
                return value
            if name == NYToyPricesConsts.END_OF_SALE_EVENT_END_DIFF:
                return eventEndTime + value

        return default

    def isPurchaseAvailable(self, toyID, serverTime, eventEndTime):
        endOfSale = self.getEndOfSale(toyID, eventEndTime)
        return True if not endOfSale else serverTime < endOfSale
