# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/goodies/goodies_cache.py
from collections import defaultdict
from typing import TYPE_CHECKING
from debug_utils import LOG_WARNING
from goodies.goodie_constants import GOODIE_VARIETY, GOODIE_STATE, GOODIE_TARGET_TYPE
from goodies.goodie_helpers import CURRENCY_TO_RESOURCE_TYPE
from gui.goodies.goodie_items import Booster, PersonalVehicleDiscount, ClanReservePresenter, DemountKit, RecertificationForm, MentoringLicense
from gui.shared.money import Money
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from typing import Optional, Dict, Tuple, List, Union
    from gui.shared.utils.requesters.GoodiesRequester import GoodieVariable
    from gui.goodies.goodie_items import _Goodie, _PersonalDiscount
    from gui.shared.utils.requesters.ShopRequester import _NamedGoodieData, _ResourceData

def _createBooster(boosterID, boosterDescription, proxy):
    return Booster(boosterID, boosterDescription, proxy)


def _createDiscount(discountID, discountDescription, proxy):
    targetType = discountDescription.target.targetType
    if targetType in _DISCOUNT_TYPES_MAPPING:
        return _DISCOUNT_TYPES_MAPPING[targetType](discountID, discountDescription, proxy)
    else:
        LOG_WARNING('Current discount with ID: %s and type: %s is not supported by UX' % (discountID, targetType))
        return None


def _createDemountKit(demountKitID, demountKitDescription, proxy):
    return DemountKit(demountKitID, demountKitDescription, proxy)


def _createRecertificationForm(recertificationFormID, recertificationFormDescription, proxy):
    return RecertificationForm(recertificationFormID, recertificationFormDescription, proxy)


def _createMentoringLicense(mentoringLicenseID, mentoringLicenseDescription, proxy):
    return MentoringLicense(mentoringLicenseID, mentoringLicenseDescription, proxy)


_GOODIES_VARIETY_MAPPING = {GOODIE_VARIETY.BOOSTER: _createBooster,
 GOODIE_VARIETY.DISCOUNT: _createDiscount,
 GOODIE_VARIETY.DEMOUNT_KIT: _createDemountKit,
 GOODIE_VARIETY.RECERTIFICATION_FORM: _createRecertificationForm,
 GOODIE_VARIETY.MENTORING_LICENSE: _createMentoringLicense}
_DISCOUNT_TYPES_MAPPING = {GOODIE_TARGET_TYPE.ON_BUY_VEHICLE: PersonalVehicleDiscount}

class GoodiesCache(IGoodiesCache):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.__goodiesCache = defaultdict(dict)
        self.__activeResourceData = None
        self.__activeBoosterTypes = None
        return

    def init(self):
        self.itemsCache.onSyncStarted += self.__clearCache

    def fini(self):
        self.itemsCache.onSyncStarted -= self.__clearCache

    def clear(self):
        self.__activeResourceData = None
        self.__activeBoosterTypes = None
        while self.__goodiesCache:
            _, cache = self.__goodiesCache.popitem()
            cache.clear()

        return

    @property
    def personalGoodies(self):
        return self._items.goodies.goodies

    def getBoosterPriceData(self, boosterID):
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
         defAltPrice)

    def isBoosterHiddenInShop(self, boosterID):
        return boosterID in self._items.shop.getHiddenBoosters()

    def getItemByTargetValue(self, targetValue):
        return self._items.getItemByCD(targetValue)

    def getActiveBoosterTypes(self):
        if self.__activeBoosterTypes is None:
            self.getActiveResources()
        return self.__activeBoosterTypes

    def getActiveResources(self):
        if self.__activeResourceData is not None:
            return self.__activeResourceData
        else:
            activeResourceData = []
            activeResourceTypes = set()
            for boosterID, boosterValues in self.personalGoodies.iteritems():
                if boosterValues.state == GOODIE_STATE.ACTIVE:
                    boosterDescription = self._items.shop.boosters.get(boosterID, None)
                    if boosterDescription:
                        resource = boosterDescription.resource
                        activeResourceData.append(resource)
                        activeResourceTypes.add(resource.resourceType)

            self.__activeBoosterTypes = activeResourceTypes
            self.__activeResourceData = activeResourceData
            return self.__activeResourceData

    def getBooster(self, boosterID):
        boosterDescription = self._items.shop.boosters.get(boosterID, None)
        return self.__makeGoodie(boosterID, boosterDescription)

    def haveBooster(self, boosterID):
        return boosterID in self._items.shop.boosters

    def getDiscount(self, discoutID):
        discountDescription = self._items.shop.discounts.get(discoutID, None)
        return self.__makeGoodie(discoutID, discountDescription)

    def getDemountKit(self, demountKitID=None, currency=None):
        return self.__getGoodieItem(demountKitID, self._items.shop.demountKits, currency)

    def getBoosters(self, criteria=REQ_CRITERIA.EMPTY):
        return self.__getGoodies(self._items.shop.boosters, criteria)

    def getDiscounts(self, criteria=REQ_CRITERIA.EMPTY):
        return self.__getGoodies(self._items.shop.discounts, criteria)

    def getDemountKits(self, criteria=REQ_CRITERIA.EMPTY):
        return self.__getGoodies(self._items.shop.demountKits, criteria)

    def getRecertificationForm(self, recertificationFormID=None, currency=None):
        return self.__getGoodieItem(recertificationFormID, self._items.shop.recertificationForms, currency)

    def getRecertificationForms(self, criteria=REQ_CRITERIA.EMPTY):
        return self.__getGoodies(self._items.shop.recertificationForms, criteria)

    def getMentoringLicenses(self, criteria=REQ_CRITERIA.EMPTY):
        return self.__getGoodies(self._items.shop.mentoringLicenses, criteria)

    def getMentoringLicense(self, mentoringLicenseFormID=None, currency=None):
        return self.__getGoodieItem(mentoringLicenseFormID, self._items.shop.mentoringLicenses, currency)

    def getGoodie(self, goodieID=None):
        return self.__makeGoodie(goodieID, self.getGoodieByID(goodieID))

    def getGoodieByID(self, goodieID):
        return self._items.shop.goodies.get(goodieID)

    def getClanReserves(self):
        result = {}
        for reserveID, reserveInfo in self._items.goodies.getActiveClanReserves().iteritems():
            guiReserveWrapper = ClanReservePresenter(reserveID, *reserveInfo)
            if guiReserveWrapper.getUsageLeftTime() > 0:
                result[reserveID] = guiReserveWrapper

        return result

    @property
    def _items(self):
        return self.itemsCache.items

    def __getGoodieItem(self, itemID, itemShopRef, currency):
        resourceType = CURRENCY_TO_RESOURCE_TYPE.get(currency, None)
        if itemID is None and resourceType is not None:
            itemID = next((id_ for id_, def_ in itemShopRef.iteritems() if def_.resource.resourceType == resourceType), None)
        description = itemShopRef.get(itemID, None)
        return self.__makeGoodie(itemID, description)

    def __getGoodies(self, goodies, criteria=REQ_CRITERIA.EMPTY):
        results = {}
        for goodieID, goodieDescription in goodies.iteritems():
            goodie = self.__makeGoodie(goodieID, goodieDescription)
            if goodie is not None and criteria(goodie):
                results[goodieID] = goodie

        return results

    def __makeGoodie(self, goodieID, goodieDescription):
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
