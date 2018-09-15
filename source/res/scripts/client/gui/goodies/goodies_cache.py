# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/goodies/goodies_cache.py
import weakref
from collections import defaultdict
from debug_utils import LOG_WARNING
from goodies.goodie_constants import GOODIE_VARIETY, GOODIE_STATE, GOODIE_TARGET_TYPE
from gui.goodies.goodie_items import Booster, PersonalVehicleDiscount
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.money import Money, MONEY_UNDEFINED
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache

def _createBooster(boosterID, boosterDescription, proxy):
    """
    Creates booster GUI instance
    """
    return Booster(boosterID, boosterDescription, proxy)


def _createDiscount(discountID, discountDescription, proxy):
    """
    Creates personal discount GUI instance.
    Right now we have only one gui instance for discounts: PersonalVehicleDiscount.
    For others discounts we don't have UX, in that case return None
    """
    targetType = discountDescription.target.targetType
    if targetType in _DISCOUNT_TYPES_MAPPING:
        return _DISCOUNT_TYPES_MAPPING[targetType](discountID, discountDescription, proxy)
    else:
        LOG_WARNING('Current discount with ID: %s and type: %s is not supported by UX' % (discountID, targetType))
        return None


_GOODIES_VARIETY_MAPPING = {GOODIE_VARIETY.BOOSTER: _createBooster,
 GOODIE_VARIETY.DISCOUNT: _createDiscount}
_DISCOUNT_TYPES_MAPPING = {GOODIE_TARGET_TYPE.ON_BUY_VEHICLE: PersonalVehicleDiscount}

class GoodiesCache(IGoodiesCache):
    """
    Global goodies cache. Contains booster and goodie GUI items.
    Uses IItemsCache.items.shop and IItemsCache.items.goodies to create goodies cache
    Listen IItemsCache events and keep cache in valid state
    """
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.__goodiesCache = defaultdict(dict)
        self.__activeBoostersTypes = None
        return

    def init(self):
        self.itemsCache.onSyncStarted += self.__clearCache

    def fini(self):
        self.itemsCache.onSyncStarted -= self.__clearCache

    def clear(self):
        self.__activeBoostersTypes = None
        while self.__goodiesCache:
            _, cache = self.__goodiesCache.popitem()
            cache.clear()

        return

    @property
    def personalGoodies(self):
        """
        Gets dynamic parts of goodies received on Account in player data. GoodiesRequester is Inventory analogue.
        """
        return self._items.goodies.goodies

    def getBoosterPriceData(self, boosterID):
        """
        Gets tuple of booster price-related data: (buy price, def price, alt price, def alt price, is booster hidden).
        """
        shop = self._items.shop
        prices = Money.makeFromMoneyTuple(shop.getBoosterPricesTuple(boosterID))
        defPrices = Money.makeFromMoneyTuple(shop.defaults.getBoosterPricesTuple(boosterID))
        if prices.isCompound():
            currency = prices.getCurrency(byWeight=True)
            buyPrice = Money.makeFrom(currency, prices.get(currency))
            defPrice = Money.makeFrom(currency, defPrices.getSignValue(currency))
            altPrice = prices.replace(currency, None)
            defAltPrice = defPrices.replace(currency, None)
        else:
            buyPrice = prices
            defPrice = defPrices
            altPrice = None
            defAltPrice = None
        return (buyPrice,
         defPrice,
         altPrice,
         defAltPrice,
         boosterID in shop.getHiddenBoosters())

    def getItemByTargetValue(self, targetValue):
        """
        Gets GUI Item by target value
        """
        return self._items.getItemByCD(targetValue)

    def getActiveBoostersTypes(self):
        """
        Gets active boosters types
        """
        if self.__activeBoostersTypes is not None:
            return self.__activeBoostersTypes
        else:
            activeBoosterTypes = []
            for boosterID, boosterValues in self.personalGoodies.iteritems():
                if boosterValues.state == GOODIE_STATE.ACTIVE:
                    boosterDescription = self._items.shop.boosters.get(boosterID, None)
                    if boosterDescription:
                        activeBoosterTypes.append(boosterDescription.resource)

            self.__activeBoostersTypes = activeBoosterTypes
            return self.__activeBoostersTypes

    def getBooster(self, boosterID):
        """
        Gets booster GUI instance
        """
        boosterDescription = self._items.shop.boosters.get(boosterID, None)
        return self.__makeGoodie(boosterID, boosterDescription)

    def getDiscount(self, discoutID):
        """
        Gets personal discount GUI instance
        """
        discountDescription = self._items.shop.discounts.get(discoutID, None)
        return self.__makeGoodie(discoutID, discountDescription)

    def getBoosters(self, criteria=REQ_CRITERIA.EMPTY):
        """
        Gets boosters GUI instances in format: {boosterID: booster, ...}
        """
        return self.__getGoodies(self._items.shop.boosters, criteria)

    def getDiscounts(self, criteria=REQ_CRITERIA.EMPTY):
        """
        Gets personal discounts GUI instances in format: {discountID: discount, ...}
        """
        return self.__getGoodies(self._items.shop.discounts, criteria)

    @property
    def _items(self):
        return self.itemsCache.items

    def __getGoodies(self, goodies, criteria=REQ_CRITERIA.EMPTY):
        """
        Gets goodies GUI instances in format: {goodieID: goodie, ...}
        """
        results = {}
        for goodieID, goodieDescription in goodies.iteritems():
            goodie = self.__makeGoodie(goodieID, goodieDescription)
            if goodie is not None and criteria(goodie):
                results[goodieID] = goodie

        return results

    def __makeGoodie(self, goodieID, goodieDescription):
        """
        Creates goodie GUI instance and adds it to cache by variety
        """
        goodie = None
        if goodieDescription is not None:
            variety = goodieDescription.variety
            container = self.__goodiesCache[variety]
            if goodieID in container:
                return container[goodieID]
            container[goodieID] = goodie = _GOODIES_VARIETY_MAPPING[variety](goodieID, goodieDescription, self)
        return goodie

    def __clearCache(self, *args):
        self.clear()
