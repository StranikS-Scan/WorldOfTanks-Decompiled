# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_reserves/personal_reserves_utils.py
import typing
from frameworks.wulf import Array
from goodies.goodie_constants import GOODIE_RESOURCE_TYPE, GOODIE_STATE, BoosterCategory
from gui.impl.common.personal_reserves.personal_reserves_shared_constants import PERSONAL_RESOURCE_ORDER, EVENT_RESOURCE_ORDER, CLAN_RESOURCE_ORDER_BY_GROUP, getAllBoosterIds
from gui.impl.common.personal_reserves.personal_reserves_shared_model_utils import getSummedBoosterCount, addBoosterModel
from gui.impl.gen.view_models.views.lobby.personal_reserves.disabled_category import DisabledCategory, CategoryType
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers.dependency import replace_none_kwargs
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from typing import List, Union, Dict
    from skeletons.gui.game_control import IBoostersController
    from skeletons.gui.shared import IItemsCache
    from gui.goodies.goodie_items import BoostersType
_BOOSTER_CATEGORY_TO_MODEL_ENUM = {BoosterCategory.PERSONAL: CategoryType.PERSONAL,
 BoosterCategory.CLAN: CategoryType.CLAN,
 BoosterCategory.EVENT: CategoryType.EVENT}

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


def addDisabledCategories(modelArray, controller):
    modelArray.clear()
    modelArray.reserve(len(BoosterCategory))
    for category in BoosterCategory:
        model = DisabledCategory()
        model.setCategoryType(_BOOSTER_CATEGORY_TO_MODEL_ENUM[category])
        model.setIsDisabled(not controller.isGameModeSupported(category))
        modelArray.addViewModel(model)
