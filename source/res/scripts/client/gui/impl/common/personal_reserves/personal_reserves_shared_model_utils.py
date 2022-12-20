# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/common/personal_reserves/personal_reserves_shared_model_utils.py
from time import time
import typing
from helpers.time_utils import ONE_YEAR, makeLocalServerTime
from collections import namedtuple, defaultdict
from goodies.goodie_constants import GOODIE_RESOURCE_TYPE, GOODIE_STATE, BoosterCategory
from gui.goodies.goodie_items import Booster, getFullNameForBoosterIcon, BoosterUICommon
from gui.impl.common.personal_reserves.personal_reserves_shared_constants import BOOST_CATEGORY_TO_RESERVE_TYPE_LOOKUP, BOOSTER_STATE_TO_BOOSTER_MODEL_STATE, PREMIUM_BOOSTER_IDS, EVENT_BOOSTER_IDS, PERSONAL_RESOURCE_ORDER, getAllBoosterIds
from gui.impl.gen.view_models.common.personal_reserves.booster_model import BoosterModel
from gui.impl.gen.view_models.common.personal_reserves.reserves_group_model import GroupCategory, ReservesGroupModel
from gui.shared.utils.requesters import RequestCriteria, REQ_CRITERIA
if typing.TYPE_CHECKING:
    from typing import Dict, List, Iterable, Optional, Union
    from skeletons.gui.goodies import IBoostersStateProvider
    from frameworks.wulf import Array

class BoosterModelData(namedtuple('BoosterModelArgs', ['resourceType',
 'category',
 'booster',
 'depotCount',
 'forcePremium'])):

    def __new__(cls, resourceType, category, booster=None, depotCount=0, forcePremium=False):
        return cls._make((resourceType,
         category,
         booster,
         depotCount,
         forcePremium))


RESERVE_GROUP_CATEGORY_LOOKUP = {GOODIE_RESOURCE_TYPE.XP: GroupCategory.XP,
 GOODIE_RESOURCE_TYPE.CREDITS: GroupCategory.CREDITS,
 GOODIE_RESOURCE_TYPE.FREE_XP_CREW_XP: GroupCategory.COMBINED_XP,
 GOODIE_RESOURCE_TYPE.FL_XP: GroupCategory.EVENT}
NO_FUTURE_GIVEN = time() + ONE_YEAR * 10

def getPersonalBoosterModelDataByResourceType(cache):
    groupedBoosterModelDataByResourceType = defaultdict(list)
    category = BoosterCategory.PERSONAL
    enabledBoosters = cache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ENABLED)
    sortedBoostersList = sorted(enabledBoosters.values(), key=lambda booster_: (booster_.finishTime if booster_.finishTime else NO_FUTURE_GIVEN, booster_.expiryTime if booster_.expiryTime else NO_FUTURE_GIVEN))
    boostersByResource = {}
    premiumBoosterArgsByResource = {}
    boosterCountByResource = {}
    setOfAlreadyRecorded = set()
    isInAccount = REQ_CRITERIA.BOOSTER.IN_ACCOUNT
    for booster in sortedBoostersList:
        resourceType = booster.boosterType
        if booster.boosterID in PREMIUM_BOOSTER_IDS:
            if booster.count != 0 or not booster.isHidden:
                premiumBoosterArgsByResource[resourceType] = BoosterModelData(resourceType=resourceType, category=category, booster=booster, depotCount=booster.count)
            continue
        if not isInAccount(booster):
            continue
        if resourceType not in setOfAlreadyRecorded:
            boostersByResource[resourceType] = booster
            setOfAlreadyRecorded.add(resourceType)
        count = boosterCountByResource.get(resourceType, 0)
        count += booster.count
        boosterCountByResource[resourceType] = count

    for resourceType in PERSONAL_RESOURCE_ORDER:
        booster = boostersByResource.get(resourceType, None)
        count = boosterCountByResource.get(resourceType, 0)
        nonPremiumBoosterArgs = BoosterModelData(resourceType=resourceType, category=category, booster=booster, depotCount=count)
        groupedBoosterModelDataByResourceType[resourceType] = [nonPremiumBoosterArgs]
        premiumBoosterArgs = premiumBoosterArgsByResource.get(resourceType)
        if premiumBoosterArgs is not None:
            groupedBoosterModelDataByResourceType[resourceType].append(premiumBoosterArgs)

    return groupedBoosterModelDataByResourceType


def addPersonalBoostersGroup(resourceType, boosterModelDataByType, groupArray):
    group = ReservesGroupModel()
    group.setCategory(RESERVE_GROUP_CATEGORY_LOOKUP[resourceType])
    boostersGroup = group.getReserves()
    for boosterModelData in boosterModelDataByType[resourceType]:
        addBoosterModel(boostersGroup, **boosterModelData._asdict())

    groupArray.addViewModel(group)


def addEventGroup(groupArray, cache):
    boosters = cache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.IN_BOOSTER_ID_LIST(EVENT_BOOSTER_IDS))
    group = ReservesGroupModel()
    group.setCategory(GroupCategory.EVENT)
    boostersGroup = group.getReserves()
    for eventBoosterId in EVENT_BOOSTER_IDS:
        booster = boosters.get(eventBoosterId, None)
        if booster is None or not booster.isReadyToUse and booster.state == GOODIE_STATE.INACTIVE:
            continue
        addBoosterModel(boostersGroup, GOODIE_RESOURCE_TYPE.FL_XP, BoosterCategory.EVENT, booster, booster.count)

    if boostersGroup:
        groupArray.addViewModel(group)
    else:
        group.unbind()
    return


def addBoosterModel(boosterArray, resourceType, category, booster=None, depotCount=0, forcePremium=False):
    model = BoosterModel()
    isPremium = booster.getIsPremium() if booster else forcePremium
    model.setIsPremium(isPremium)
    iconId = getFullNameForBoosterIcon(resourceType, isPremium=isPremium)
    model.setIconId(iconId)
    model.setReserveType(BOOST_CATEGORY_TO_RESERVE_TYPE_LOOKUP[category])
    model.setInDepot(depotCount)
    if booster:
        boosterID = booster.boosterID
        model.setBoosterID(boosterID)
        model.setInactivationTime(makeLocalServerTime(booster.finishTime) or 0)
        model.setState(BOOSTER_STATE_TO_BOOSTER_MODEL_STATE[booster.state])
        model.setTotalDuration(booster.effectTime)
        expiry = booster.expiryTime
        if expiry is not None:
            model.setExpiryTime(expiry)
        if isinstance(booster, Booster):
            model.price.assign(booster.getBuyPrice())
        maxEffect, minEffect = makeBonuses(booster)
        model.setMinBonus(minEffect)
        model.setMaxBonus(maxEffect)
    boosterArray.addViewModel(model)
    return


def makeBonuses(booster):
    bonus = booster.effectValue or [0]
    if isinstance(bonus, list):
        bonus = set(bonus)
        if len(bonus) > 1:
            return (max(bonus), min(bonus))
        bonus = bonus.pop()
    return (0, bonus)


def getTotalBoostersByResourceAndPremium(booster, cache):
    return 0 if booster is None else getSummedBoosterCount(criteria=RequestCriteria(REQ_CRITERIA.BOOSTER.BOOSTER_TYPES([booster.boosterType]), REQ_CRITERIA.BOOSTER.BOOSTER_CATEGORIES([booster.category]), REQ_CRITERIA.BOOSTER.IN_BOOSTER_ID_LIST(PREMIUM_BOOSTER_IDS if booster.boosterID in PREMIUM_BOOSTER_IDS else getAllBoosterIds() - set(PREMIUM_BOOSTER_IDS))), cache=cache)


def getSummedBoosterCount(criteria, cache, filter_=None):
    boosters = cache.getBoosters(criteria=criteria).values()
    return sum((booster.count for booster in boosters if not filter_ or filter_(booster)))
