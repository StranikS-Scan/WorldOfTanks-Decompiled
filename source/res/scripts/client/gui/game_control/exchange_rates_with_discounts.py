# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/exchange_rates_with_discounts.py
import logging
import math
from abc import abstractmethod, ABCMeta
from Event import Event, EventManager
from exchange.personal_discounts_constants import EXCHANGE_RATE_GOLD_NAME, EXCHANGE_RATE_FREE_XP_NAME, EXCHANGE_NAME_TO_GAME_PARAM_NAME, ExchangeRate
from exchange import personal_discounts_parser, personal_discounts_helper
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.lobby.exchange.exchange_rates_helper import getRateNameFromCurrencies, getExchangeRate
from helpers import dependency, time_utils
from helpers.server_settings import _ExchangeRatesConfig
from skeletons.gui.game_control import IExchangeRatesWithDiscountsProvider, IExchangeRateWithDiscounts
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
UNINITIALIZED_CACHE = -1

def getCurrentTime():
    return time_utils.getServerUTCTime()


def _filterTokensWithSubStr(tokensDict, template):
    return {key:value for key, value in tokensDict.items() if key.startswith(template)}


class ExchangeRateWithDiscounts(IExchangeRateWithDiscounts):
    __metaclass__ = ABCMeta
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    _EXCHANGE_NAME = None

    def __init__(self, exchangeName=None):
        self.__allAvailableDiscounts = UNINITIALIZED_CACHE
        self.__commonDiscount = UNINITIALIZED_CACHE
        self.__em = EventManager()
        self._exchangeName = exchangeName or self._EXCHANGE_NAME
        self.onUpdated = Event(self.__em)

    def init(self):
        g_clientUpdateManager.addCallback('tokens', self.__onTokensUpdate)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onSettingsChanged
        self._invalidateCache()

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self, True)
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onSettingsChanged
        self._invalidateCache()
        self.__em.clear()

    @property
    def getExchangeRateName(self):
        return self._exchangeName

    @property
    def discountInfo(self):
        if not self.isDiscountAvailable():
            return None
        else:
            return self.__personalLimitedDiscountInfo if self.__isPersonalLimitedDiscountAvailable() else self.unlimitedDiscountInfo

    @property
    def unlimitedDiscountInfo(self):
        if self.__commonDiscount == UNINITIALIZED_CACHE:
            self.__createDiscounts()
        return self.__commonDiscount

    @property
    def allPersonalLimitedDiscounts(self):
        if self.__allAvailableDiscounts == UNINITIALIZED_CACHE:
            self.__createDiscounts()
        return self.__allAvailableDiscounts

    @property
    def unlimitedDiscountRate(self):
        if self.__isAnyUnlimitedDiscountAvailable():
            rate = ExchangeRate(goldRateValue=self.unlimitedDiscountInfo.goldRateValue, resourceRateValue=self.unlimitedDiscountInfo.resourceRateValue)
            return rate
        return self.defaultRate

    @property
    def discountRate(self):
        if self.__isPersonalLimitedDiscountAvailable():
            return self.__personalLimitedDiscountRate
        return self.unlimitedDiscountRate if self.__isAnyUnlimitedDiscountAvailable() else self._exchangeRate

    @property
    def bestPersonalDiscount(self):
        limitedPersonalDiscount = self.__personalLimitedDiscountInfo
        if limitedPersonalDiscount is None:
            unlimitedDiscount = self.unlimitedDiscountInfo
            if unlimitedDiscount is not None and unlimitedDiscount.isPersonal:
                return unlimitedDiscount
            return
        else:
            return limitedPersonalDiscount

    @property
    def commonServerDiscountRate(self):
        serverDiscount = self._commonServerDiscountInfo
        return ExchangeRate(goldRateValue=serverDiscount.goldRateValue, resourceRateValue=serverDiscount.resourceRateValue) if serverDiscount is not None else self.defaultRate

    @property
    def unlimitedRateAfterMainDiscount(self):
        return self.unlimitedDiscountRate if self.__isPersonalLimitedDiscountAvailable() else self.defaultRate

    @property
    def defaultRate(self):
        return self._getExchangeRateObject(self._getRate(self._ratesRequester.defaults))

    @property
    def exchangeDiscountPercent(self):
        defaultRate = float(self.defaultRate.resourceRateValue / self.defaultRate.goldRateValue)
        discountRate = float(self.discountRate.resourceRateValue / self.discountRate.goldRateValue)
        return math.floor(float(discountRate - defaultRate) / defaultRate * 100)

    def isDiscountAvailable(self):
        return self.__isPersonalLimitedDiscountAvailable() or self.__isAnyUnlimitedDiscountAvailable()

    def calculateExchange(self, goldAmount):
        return personal_discounts_helper.calculateGoldExchangeWithDiscounts(self._allDiscounts, goldAmount, self.defaultRate, getCurrentTime())

    def calculateGoldToExchange(self, resourceAmount):
        return self.calculateResourceToExchange(resourceAmount)[0]

    def calculateResourceToExchange(self, resourceAmount):
        return personal_discounts_helper.calculateResourceExchangeWithDiscounts(self._allDiscounts, resourceAmount, self.defaultRate, getCurrentTime())

    @abstractmethod
    def isPersonalDiscountConfigEnabled(self):
        pass

    @abstractmethod
    def _getExchangeRateObject(self, rate):
        pass

    @property
    def _allDiscounts(self):
        discounts = self.allPersonalLimitedDiscounts[:]
        if self.unlimitedDiscountInfo is not None:
            discounts.append(self.unlimitedDiscountInfo)
        return discounts

    @property
    def _exchangeRate(self):
        return self._getExchangeRateObject(self._getRate(self._ratesRequester))

    def _getRate(self, proxy):
        rate = EXCHANGE_NAME_TO_GAME_PARAM_NAME.get(self._exchangeName, None)
        return getattr(proxy, rate) if rate is not None else None

    @property
    def _commonServerDiscountInfo(self):
        return personal_discounts_helper.createCommonDiscount(self._exchangeName, self._exchangeRate) if self.defaultRate != self._exchangeRate else None

    @property
    def _config(self):
        return self.__lobbyContext.getServerSettings().exchangeRates if self.__lobbyContext else _ExchangeRatesConfig()

    @property
    def _ratesRequester(self):
        return self.__itemsCache.items.shop

    def _invalidateCache(self):
        self.__allAvailableDiscounts = UNINITIALIZED_CACHE
        self.__commonDiscount = UNINITIALIZED_CACHE

    def _exchangeRateUpdated(self, *args, **kwargs):
        self._invalidateCache()
        self.onUpdated()

    def __isAnyUnlimitedDiscountAvailable(self):
        return bool(self.unlimitedDiscountInfo)

    @property
    def __personalLimitedDiscountRate(self):
        if self.__isPersonalLimitedDiscountAvailable():
            rate = ExchangeRate(goldRateValue=self.__personalLimitedDiscountInfo.goldRateValue, resourceRateValue=self.__personalLimitedDiscountInfo.resourceRateValue)
            return rate
        return self.unlimitedDiscountRate

    def __isPersonalLimitedDiscountAvailable(self):
        return self.__personalLimitedDiscountInfo is not None and self.__isPersonalDiscountTheBestDiscount() and self.isPersonalDiscountConfigEnabled()

    @property
    def __personalLimitedDiscountInfo(self):
        if self.__allAvailableDiscounts == UNINITIALIZED_CACHE:
            self.__createDiscounts()
        return self.allPersonalLimitedDiscounts[0] if self.__allAvailableDiscounts else None

    def __isPersonalDiscountTheBestDiscount(self):
        if self.__personalLimitedDiscountInfo is not None:
            commonDiscount = self.unlimitedDiscountInfo
            if commonDiscount is None:
                return True
            sortedDiscounts = personal_discounts_helper.sortExchangeRatesDiscounts([commonDiscount, self.__personalLimitedDiscountInfo])
            if sortedDiscounts:
                return sortedDiscounts[0] == self.__personalLimitedDiscountInfo
        return False

    def __onTokensUpdate(self, diff):
        if _filterTokensWithSubStr(diff, self._exchangeName) and self.isPersonalDiscountConfigEnabled():
            self._exchangeRateUpdated()

    def __onSettingsChanged(self, diff):
        if 'exchange_rates_config' in diff:
            self._exchangeRateUpdated()

    def __createDiscounts(self):
        discounts = []
        if self._commonServerDiscountInfo is not None:
            discounts.append(self._commonServerDiscountInfo)
        tokens = self.__getDiscountTokens(self._exchangeName)
        if tokens and self.isPersonalDiscountConfigEnabled():
            personalDiscounts = personal_discounts_parser.convertTokensToExchangeDiscounts(tokens, getExchangeRate(self._exchangeName, default=True), currentTime=getCurrentTime())
            if personalDiscounts is not None:
                discounts.extend(personalDiscounts)
        if discounts:
            allSortedDiscounts = personal_discounts_helper.sortExchangeRatesDiscounts(discounts)
            personal, common = personal_discounts_helper.getPersonalDiscountsAndCommonDiscount(allSortedDiscounts)
            self.__allAvailableDiscounts = personal or []
            self.__commonDiscount = common
        else:
            self.__allAvailableDiscounts, self.__commonDiscount = [], None
        return

    def __getDiscountTokens(self, tokenStart):
        return _filterTokensWithSubStr(self.__itemsCache.items.tokens.getTokens(), tokenStart)


class GoldExchangeRateWithDiscounts(ExchangeRateWithDiscounts):
    _EXCHANGE_NAME = EXCHANGE_RATE_GOLD_NAME

    def init(self):
        g_clientUpdateManager.addCallback('shop.exchangeRate', self._exchangeRateUpdated)
        super(GoldExchangeRateWithDiscounts, self).init()

    def _getExchangeRateObject(self, rate):
        return ExchangeRate(goldRateValue=rate[0], resourceRateValue=rate[1])

    def isPersonalDiscountConfigEnabled(self):
        return self._config.isGoldExchangePesronalDiscountsAvailable

    def _getRate(self, proxy):
        rate = EXCHANGE_NAME_TO_GAME_PARAM_NAME.get(self._exchangeName, None)
        return (1, getattr(proxy, rate)) if rate is not None else None


class XpTranslationRateWithDiscounts(ExchangeRateWithDiscounts):
    _EXCHANGE_NAME = EXCHANGE_RATE_FREE_XP_NAME

    def init(self):
        g_clientUpdateManager.addCallback('shop.freeXPConversion', self._exchangeRateUpdated())
        super(XpTranslationRateWithDiscounts, self).init()

    def _getExchangeRateObject(self, rate):
        return ExchangeRate(goldRateValue=rate[1], resourceRateValue=rate[0])

    def isPersonalDiscountConfigEnabled(self):
        return self._config.isExperienceExchangePesronalDiscountsAvailable


class ExchangeRatesWithDiscountsProvider(IExchangeRatesWithDiscountsProvider):

    def __init__(self):
        self.__goldToCredits = GoldExchangeRateWithDiscounts()
        self.__freeXpTranslation = XpTranslationRateWithDiscounts()

    def onLobbyInited(self, event):
        self.goldToCredits.init()
        self.freeXpTranslation.init()
        super(ExchangeRatesWithDiscountsProvider, self).onLobbyInited(event)

    def onDisconnected(self):
        self.goldToCredits.fini()
        self.freeXpTranslation.fini()
        super(ExchangeRatesWithDiscountsProvider, self).onDisconnected()

    def onAvatarBecomePlayer(self):
        self.goldToCredits.fini()
        self.freeXpTranslation.fini()
        super(ExchangeRatesWithDiscountsProvider, self).onAvatarBecomePlayer()

    def fini(self):
        self.__clear()
        super(ExchangeRatesWithDiscountsProvider, self).fini()

    @property
    def goldToCredits(self):
        return self.__goldToCredits

    @property
    def freeXpTranslation(self):
        return self.__freeXpTranslation

    def get(self, rateType):
        if rateType == EXCHANGE_RATE_GOLD_NAME:
            return self.goldToCredits
        else:
            return self.freeXpTranslation if rateType == EXCHANGE_RATE_FREE_XP_NAME else None

    def exchange(self, currency, toCurrency, amount):
        exchangeName = getRateNameFromCurrencies((currency, toCurrency))
        if exchangeName is None:
            _logger.error('Exchange type is undefined for %s, %s', currency, toCurrency)
            return
        else:
            return self.get(exchangeName).calculateExchange(amount)

    def __clear(self):
        self.goldToCredits.fini()
        self.freeXpTranslation.fini()
        self.__goldToCredits = None
        self.__freeXpTranslation = None
        return
