# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_reserves/personal_reserves_utils.py
import typing
from frameworks.wulf import Array
from goodies.goodie_constants import GOODIE_RESOURCE_TYPE, GOODIE_STATE
from gui.goodies.goodies_constants import BoosterCategory
from gui.impl.common.personal_reserves.personal_reserves_shared_constants import PERSONAL_RESOURCE_ORDER, EVENT_RESOURCE_ORDER, CLAN_RESOURCE_ORDER_BY_GROUP, getAllBoosterIds
from gui.impl.common.personal_reserves.personal_reserves_shared_model_utils import getSummedBoosterCount, addBoosterModel
from gui.shared.utils.requesters import REQ_CRITERIA
if typing.TYPE_CHECKING:
    from typing import List, Union, Dict
    from skeletons.gui.goodies import IGoodiesCache
    from skeletons.gui.shared import IItemsCache
    from skeletons.gui.web import IWebController
    from gui.goodies.goodie_items import BoostersType

def getActiveBoosters(goodiesCache, webController):
    criteria = REQ_CRITERIA.BOOSTER.ACTIVE
    activeBoosters = goodiesCache.getBoosters(criteria=criteria).values()
    if webController.getAccountProfile().isInClan():
        clanBoosters = [ clanBooster for clanBooster in goodiesCache.getClanReserves().values() if clanBooster.state == GOODIE_STATE.ACTIVE ]
        activeBoosters.extend(clanBoosters)
    return activeBoosters


def addToReserveArrayByCategory(reservesArray, boosters, category, cache, canAddEmpty=False):
    boosters = [ booster for booster in boosters if booster.category == category ]
    if not boosters and not canAddEmpty:
        return
    else:
        boostersByResourceType = {booster.boosterType:booster for booster in boosters}
        resourceTypeOrder = getGUIResourceOrder(category, boostersByResourceType)
        for resourceType in resourceTypeOrder:
            addBoosterModel(reservesArray, resourceType, category, booster=boostersByResourceType.get(resourceType, None), depotCount=getTotalBoostersByResourceType(category, resourceType, cache))

        return


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


def getTotalBoostersByResourceType(category, resourceType, cache):
    return getSummedBoosterCount(criteria=REQ_CRITERIA.BOOSTER.BOOSTER_TYPES([resourceType]) | REQ_CRITERIA.BOOSTER.BOOSTER_CATEGORIES([category]), cache=cache)


def boostersInClientUpdate(diff):
    return set(diff.get('goodies', {}).keys()).intersection(getAllBoosterIds()) or diff.get('cache', {}).get('activeOrders', {})


def canBuyBooster(booster, itemsCache):
    return booster.mayPurchase(itemsCache.items.stats.money)
