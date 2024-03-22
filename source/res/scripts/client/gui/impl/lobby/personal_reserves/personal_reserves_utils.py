# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_reserves/personal_reserves_utils.py
import typing
from frameworks.wulf import Array
from goodies.goodie_constants import GOODIE_RESOURCE_TYPE, GOODIE_STATE, BoosterCategory
from gui.impl.common.personal_reserves.personal_reserves_shared_constants import PERSONAL_RESOURCE_ORDER, EVENT_RESOURCE_ORDER, CLAN_RESOURCE_ORDER_BY_GROUP, PREMIUM_BOOSTER_IDS
from gui.impl.gen.view_models.views.lobby.personal_reserves.disabled_category import DisabledCategory, CategoryType
from gui.shared.utils.requesters import REQ_CRITERIA, RequestCriteria
from helpers.dependency import replace_none_kwargs
from helpers.time_utils import ONE_DAY
from skeletons.gui.goodies import IGoodiesCache, IBoostersStateProvider
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from typing import List, Union, Dict, Tuple
    from skeletons.gui.game_control import IBoostersController
    from skeletons.gui.shared import IItemsCache
    from gui.goodies.goodie_items import BoostersType, Booster, BoosterUICommon
_BOOSTER_CATEGORY_TO_MODEL_ENUM = {BoosterCategory.PERSONAL: CategoryType.PERSONAL,
 BoosterCategory.CLAN: CategoryType.CLAN,
 BoosterCategory.EVENT: CategoryType.EVENT}

def generatePersonalReserveTick(boosters):
    if not boosters:
        return 0
    nextInterval = ONE_DAY
    for booster in boosters:
        timeLeftTO24Hour = booster.getTimeLeftToNextExpiry() - ONE_DAY
        if 0 < timeLeftTO24Hour < nextInterval:
            nextInterval = timeLeftTO24Hour
        activationTimeLeft = booster.getUsageLeftTime()
        if 0 < activationTimeLeft < nextInterval:
            nextInterval = activationTimeLeft

    return nextInterval if nextInterval < ONE_DAY else 0


@replace_none_kwargs(goodiesCache=IGoodiesCache, webController=IWebController)
def getActiveBoosters(goodiesCache, webController):
    criteria = REQ_CRITERIA.BOOSTER.ACTIVE
    activeBoosters = goodiesCache.getBoosters(criteria=criteria).values()
    activeBoosters.extend(getActiveClanBoosters(cache=goodiesCache, controller=webController))
    return activeBoosters


@replace_none_kwargs(cache=IGoodiesCache, controller=IWebController)
def getActiveClanBoosters(cache=None, controller=None):
    if controller.getAccountProfile().isInClan():
        clanBoosters = [ clanBooster for clanBooster in cache.getClanReserves().values() if clanBooster.state == GOODIE_STATE.ACTIVE ]
        return clanBoosters
    return []


@replace_none_kwargs(cache=IGoodiesCache)
def isCategoryActive(category, cache=None):
    if category is BoosterCategory.CLAN:
        return bool(getActiveClanBoosters())
    criteria = REQ_CRITERIA.BOOSTER.BOOSTER_CATEGORIES([category]) | REQ_CRITERIA.BOOSTER.ACTIVE
    return bool(cache.getBoosters(criteria=criteria).values())


def getGUIResourceOrder(category, boostersByResource):
    if category == BoosterCategory.PERSONAL:
        return PERSONAL_RESOURCE_ORDER
    if category == BoosterCategory.EVENT:
        return EVENT_RESOURCE_ORDER
    resourceOrder = [CLAN_RESOURCE_ORDER_BY_GROUP[0][0], CLAN_RESOURCE_ORDER_BY_GROUP[1][0]]
    for idx, group in enumerate(CLAN_RESOURCE_ORDER_BY_GROUP):
        for resourceType in group:
            if resourceType in boostersByResource:
                resourceOrder[idx] = resourceType
                break

    return resourceOrder


def getTotalReadyReserves(cache):
    return getSummedBoosterCount(criteria=REQ_CRITERIA.BOOSTER.IS_READY_TO_ACTIVATE, cache=cache)


def getTotalLimitedReserves(cache):
    return getSummedBoosterCount(criteria=REQ_CRITERIA.BOOSTER.LIMITED, cache=cache)


def getTotalLimitedBoostersByResourceType(category, resourceType, cache):
    return getSummedBoosterCount(criteria=REQ_CRITERIA.BOOSTER.BOOSTER_TYPES([resourceType]) | REQ_CRITERIA.BOOSTER.BOOSTER_CATEGORIES([category]) | REQ_CRITERIA.BOOSTER.LIMITED | REQ_CRITERIA.BOOSTER.ENABLED, cache=cache)


def getNearestExpiryTimeForToday(cache):
    expiringBoosters = cache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.LIMITED | REQ_CRITERIA.BOOSTER.IS_READY_TO_ACTIVATE).values()
    nearestExpiringTime, _ = getNearestExpirationTimeAndCountForToday(expiringBoosters)
    return nearestExpiringTime


def getTotalBoostersByResourceType(category, resourceType, cache):
    return getSummedBoosterCount(criteria=REQ_CRITERIA.BOOSTER.BOOSTER_TYPES([resourceType]) | REQ_CRITERIA.BOOSTER.BOOSTER_CATEGORIES([category]) | REQ_CRITERIA.BOOSTER.ENABLED, cache=cache)


def getNearestExpirationTimeAndCountForToday(boosters):
    if not boosters:
        return (0, 0)
    nearestExpiringTime = findNearestExpiryTimeInBoostersList(boosters)
    counter = sum((booster.expirations[nearestExpiringTime].amount for booster in boosters if nearestExpiringTime in booster.expirations))
    return (nearestExpiringTime, counter)


def findNearestExpiryTimeInBoostersList(goodies):
    if not goodies:
        return 0
    expirations = [ goodie.nextExpiryTime for goodie in goodies if goodie.nextExpiryTime > 0 ]
    nearestExpiringTime = min(expirations or [0])
    return nearestExpiringTime


def getNearestExpiryTimeAndAmountByGroup(category, resourceType, cache):
    boosters = cache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.BOOSTER_TYPES([resourceType]) | REQ_CRITERIA.BOOSTER.BOOSTER_CATEGORIES([category]) | REQ_CRITERIA.BOOSTER.LIMITED).values()
    return getNearestExpirationTimeAndCountForToday(boosters)


def canBuyBooster(booster, itemsCache):
    return booster.mayPurchase(itemsCache.items.stats.money)


def addDisabledCategories(modelArray, controller):
    modelArray.clear()
    modelArray.reserve(len(BoosterCategory))
    for category in BoosterCategory:
        model = DisabledCategory()
        model.setCategoryType(_BOOSTER_CATEGORY_TO_MODEL_ENUM[category])
        model.setIsDisabled(not controller.isGameModeSupported(category))
        modelArray.addViewModel(model)


def getTotalBoostersByResourceAndPremium(booster, cache):
    if booster is None:
        return 0
    else:
        criteria = REQ_CRITERIA.BOOSTER.BOOSTER_TYPES([booster.boosterType]) | REQ_CRITERIA.BOOSTER.BOOSTER_CATEGORIES([booster.category]) | REQ_CRITERIA.BOOSTER.ENABLED
        if booster.boosterID in PREMIUM_BOOSTER_IDS:
            criteria |= REQ_CRITERIA.BOOSTER.IN_BOOSTER_ID_LIST(PREMIUM_BOOSTER_IDS)
        else:
            criteria |= ~REQ_CRITERIA.BOOSTER.IN_BOOSTER_ID_LIST(PREMIUM_BOOSTER_IDS)
        return getSummedBoosterCount(criteria=criteria, cache=cache)


def getSummedBoosterCount(criteria, cache, filter_=None):
    boosters = cache.getBoosters(criteria=criteria).values()
    return sum((booster.count for booster in boosters if not filter_ or filter_(booster)))


def getBoostersInGroup(booster, cache):
    criteria = REQ_CRITERIA.BOOSTER.BOOSTER_TYPES([booster.boosterType]) | REQ_CRITERIA.BOOSTER.BOOSTER_CATEGORIES([booster.category]) | REQ_CRITERIA.BOOSTER.IN_ACCOUNT | REQ_CRITERIA.BOOSTER.ENABLED
    if booster.boosterID in PREMIUM_BOOSTER_IDS:
        criteria |= REQ_CRITERIA.BOOSTER.IN_BOOSTER_ID_LIST(PREMIUM_BOOSTER_IDS)
    else:
        criteria |= ~REQ_CRITERIA.BOOSTER.IN_BOOSTER_ID_LIST(PREMIUM_BOOSTER_IDS)
    boosters = cache.getBoosters(criteria).values()
    if boosters:
        boosters = sorted(boosters, key=lambda booster_: (booster_.isExpirable, 9999999999L - booster_.nextExpiryTime), reverse=True)
    return boosters
